"""Create the reference-inspired mug inside a FreeCAD GUI session.

Run with MCP Bridge's execute_python_file tool, or open this file in FreeCAD.
Dimensions are in millimetres. The output uses native sketches and features.
"""

import json
from pathlib import Path

import FreeCAD as App
import FreeCADGui as Gui
import Part


OUTPUT = Path(__file__).resolve().parent / "Mug.FCStd"
OUTER_RADIUS = 41.0
WALL = 3.0
BASE = 4.0
STRAIGHT_START = 65.0
RIM_START = 99.0
HANDLE_RADIUS = 3.6


def point(x, y):
    return App.Vector(x, y, 0)


def bezier(poles):
    curve = Part.BezierCurve()
    curve.setPoles([point(x, y) for x, y in poles])
    return curve.toBSpline()


def check_solid(feature):
    shape = feature.Shape
    if "Invalid" in feature.State or "Touched" in feature.State:
        raise RuntimeError(f"{feature.Label}: {feature.getStatusString()}")
    if shape.isNull() or not shape.isValid() or len(shape.Solids) != 1:
        raise RuntimeError(f"{feature.Label} must be one valid solid")
    if shape.Volume <= 0:
        raise RuntimeError(f"{feature.Label} has no positive volume")


def create_mug():
    if OUTPUT.exists() or "Mug" in App.listDocuments():
        raise RuntimeError("A Mug file or document already exists; refusing to overwrite it")

    doc = App.newDocument("Mug")
    doc.Label = "Mug — curved ceramic style"
    doc.openTransaction("Create reference-inspired mug")
    try:
        body = doc.addObject("PartDesign::Body", "MugBody")
        body.Label = "Mug"

        # Sketch x is radial distance; sketch y becomes world z (height).
        xz_plane = App.Placement(App.Vector(), App.Rotation(App.Vector(1, 0, 0), 90))
        profile = doc.addObject("Sketcher::SketchObject", "CupProfile")
        body.addObject(profile)
        profile.Label = "Cup wall, rounded lip, and base"
        profile.Placement = xz_plane
        inner = OUTER_RADIUS - WALL
        profile.addGeometry([
            Part.LineSegment(point(0, 0), point(28, 0)),
            bezier([(28, 0), (38, 0), (OUTER_RADIUS, 28), (OUTER_RADIUS, STRAIGHT_START)]),
            Part.LineSegment(point(OUTER_RADIUS, STRAIGHT_START), point(OUTER_RADIUS, RIM_START)),
            Part.Arc(point(OUTER_RADIUS, RIM_START),
                     point(OUTER_RADIUS - WALL / 2, RIM_START + WALL / 2),
                     point(inner, RIM_START)),
            Part.LineSegment(point(inner, RIM_START), point(inner, STRAIGHT_START)),
            bezier([(inner, STRAIGHT_START), (inner, 31), (35, BASE), (27, BASE)]),
            Part.LineSegment(point(27, BASE), point(0, BASE)),
            Part.LineSegment(point(0, BASE), point(0, 0)),
        ], False)

        cup = body.newObject("PartDesign::Revolution", "CupRevolution")
        cup.Label = "Revolved hollow cup"
        cup.Profile = profile
        cup.ReferenceAxis = (profile, ["V_Axis"])
        cup.Angle = 360
        cup.Refine = True
        doc.recompute()
        check_solid(cup)

        path = doc.addObject("Sketcher::SketchObject", "HandlePath")
        body.addObject(path)
        path.Label = "Curved handle centreline"
        path.Placement = xz_plane
        # Shared end tangents give smooth joins without interpolation overshoot.
        curve = Part.BSplineCurve()
        curve.buildFromPolesMultsKnots(
            [point(x, z) for x, z in [
                (39.5, 81), (48, 84.4), (65, 94), (72, 79),
                (79, 64), (69, 47), (57, 36),
                (45, 25), (41.5, 22.1), (37, 23),
            ]],
            [4, 3, 3, 4], [0.0, 1.0, 2.0, 3.0], False, 3,
        )
        if not curve.removeKnot(2, 2, 1e-7) or not curve.removeKnot(3, 2, 1e-7):
            raise RuntimeError("Handle spline joins must be tangent-continuous")
        path.addGeometry(curve, False)

        section = doc.addObject("Sketcher::SketchObject", "HandleSection")
        body.addObject(section)
        section.Label = "Handle round section — diameter 7.2 mm"
        tangent = curve.tangent(curve.FirstParameter)[0]
        section.Placement = App.Placement(
            App.Vector(39.5, 0, 81),
            App.Rotation(App.Vector(0, 0, 1), App.Vector(tangent.x, 0, tangent.y)),
        )
        section.addGeometry(Part.Circle(App.Vector(), App.Vector(0, 0, 1), HANDLE_RADIUS), False)

        handle = body.newObject("PartDesign::AdditivePipe", "HandleSweep")
        handle.Label = "Swept handle joined to cup"
        handle.Profile = section
        handle.Spine = (path, ["Edge1"])
        handle.Refine = True
        doc.recompute()
        check_solid(handle)

        junctions = [
            f"Edge{i}" for i, edge in enumerate(handle.Shape.Edges, 1)
            if 10 < edge.Length < 14 and edge.CenterOfMass.x > 37
            and 15 < edge.CenterOfMass.z < 90 and edge.BoundBox.YLength > 3
        ]
        if len(junctions) != 4:
            raise RuntimeError("Could not identify both handle attachment loops")
        finish = body.newObject("PartDesign::Fillet", "HandleBlends")
        finish.Label = "Rounded handle attachments — 1.5 mm"
        finish.Base = (handle, junctions)
        finish.Radius = 1.5
        doc.recompute()
        check_solid(finish)

        # The swept handle must not leave material inside the drinking cavity.
        v = lambda radius, height: App.Vector(radius, 0, height)
        inner_curve = Part.BezierCurve()
        inner_curve.setPoles([v(27, BASE), v(35, BASE), v(inner, 31), v(inner, STRAIGHT_START)])
        cavity_wire = Part.Wire([
            Part.makeLine(v(0, BASE), v(27, BASE)), inner_curve.toShape(),
            Part.makeLine(v(inner, STRAIGHT_START), v(inner, RIM_START + WALL)),
            Part.makeLine(v(inner, RIM_START + WALL), v(0, RIM_START + WALL)),
            Part.makeLine(v(0, RIM_START + WALL), v(0, BASE)),
        ])
        cavity = Part.Face(cavity_wire).revolve(App.Vector(), App.Vector(0, 0, 1), 360)
        if finish.Shape.common(cavity).Volume > 0.001:
            raise RuntimeError("The handle must not protrude into the cup cavity")

        for feature in (profile, cup, path, section, handle):
            feature.Visibility = False
        finish.Visibility = True
        body.Tip = finish
        finish.ViewObject.ShapeColor = (0.86, 0.85, 0.79)
        finish.ViewObject.LineColor = (0.40, 0.39, 0.35)
        finish.ViewObject.DisplayMode = "Shaded"
        finish.ViewObject.Deviation = 0.05
        finish.ViewObject.AngularDeflection = 8
        doc.recompute()
        doc.commitTransaction()
    except Exception:
        doc.abortTransaction()
        raise

    view = Gui.activeDocument().activeView()
    view.setActiveObject("pdbody", body)
    Gui.Selection.clearSelection()
    view.setCameraOrientation(App.Rotation(
        App.Vector(1, 0, 0), App.Vector(0, 0, 1),
        App.Vector(0.12, -1, 0.28), "ZYX",
    ).Q)
    view.fitAll()
    doc.recompute()
    check_solid(finish)
    doc.saveAs(str(OUTPUT))
    Part.export([body], str(OUTPUT.with_suffix(".step")))
    view.saveImage(str(OUTPUT.with_suffix(".png")), 1100, 1000, "White")
    print(json.dumps({
        "document": doc.Name,
        "body": body.Name,
        "tip": body.Tip.Name,
        "valid": finish.Shape.isValid(),
        "solids": len(finish.Shape.Solids),
        "material_volume_mm3": round(finish.Shape.Volume, 2),
        "height_mm": round(finish.Shape.BoundBox.ZLength, 2),
        "width_with_handle_mm": round(finish.Shape.BoundBox.XLength, 2),
        "output": str(OUTPUT),
    }, indent=2))


if __name__ == "__main__":
    create_mug()
