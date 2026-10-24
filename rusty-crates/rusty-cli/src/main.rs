//https://www.youtube.com/watch?v=5UA9UWWAagc&t=6s
use clap::Parser;
use jiff::Zoned;
use owo_colors::OwoColorize;
use serde::Serialize;
use std::{
    fs,
    path::{Path, PathBuf},
};
use strum::Display;
use tabled::{
    Tabled,
    settings::{Color, object::Columns, object::Rows},
};

#[derive(Debug, Display, Serialize)]
enum EntryType {
    File,
    Directory,
}

#[derive(Debug, Tabled, Serialize)]
struct FileEntry {
    #[tabled(rename = "Name")]
    name: String,
    #[tabled(rename = "Type")]
    entry_type: EntryType,
    #[tabled(rename = "Size B")]
    len_bytes: u64,
    #[tabled(rename = "Modified")]
    modified: String,
}

#[derive(Debug, Parser)]
#[command(author, version, about, long_about = "CLI - Formatted ls.")]
struct Cli {
    path: Option<PathBuf>,
    #[arg(short, long, default_value_t = false, help = "Output in JSON format")]
    json: bool,
}

fn main() {
    let cli = Cli::parse();
    let path = cli.path.unwrap_or_else(|| PathBuf::from("."));

    if let Ok(does_exist) = fs::exists(&path) {
        if does_exist {
            let get_files = get_files(&path);
            if cli.json {
                match serde_json::to_string_pretty(&get_files) {
                    Ok(json_output) => println!("{}", json_output),
                    Err(e) => eprintln!("Failed to serialize to JSON: {}", e),
                }
            } else {
                print_as_table(&get_files);
            }
        } else {
            println!("Path does not exist: {}", path.display().red());
        }
    } else {
        println!("Failed to check if path exists: {}", path.display().red());
    }
}

fn print_as_table(get_files: &Vec<FileEntry>) {
    let mut table = tabled::Table::new(get_files);
    table.with(tabled::settings::Style::rounded());
    table.modify(
        tabled::settings::object::Columns::first(),
        tabled::settings::Color::FG_BRIGHT_CYAN,
    );
    table.modify(Columns::one(2), Color::FG_BRIGHT_MAGENTA);
    table.modify(Columns::one(3), Color::FG_BRIGHT_YELLOW);
    table.modify(Rows::first(), Color::FG_BRIGHT_GREEN);
    println!("{}", table.to_string());
}

fn get_files(path: &Path) -> Vec<FileEntry> {
    let mut files = Vec::default();
    match fs::read_dir(path) {
        Ok(entries) => {
            for entry in entries {
                if let Ok(dir_entry) = entry {
                    push_file_meta(&mut files, dir_entry);
                }
            }
        }
        Err(e) => {
            println!(
                "Failed to read directory: {}. {}",
                path.display().red(),
                e.red()
            );
        }
    }

    files
}

fn push_file_meta(files: &mut Vec<FileEntry>, dir_entry: fs::DirEntry) {
    if let Ok(file_meta) = dir_entry.metadata() {
        files.push(FileEntry {
            name: dir_entry
                .file_name()
                .into_string()
                .unwrap_or_else(|_| "Invalid UTF-8".to_string()),
            entry_type: file_meta
                .is_dir()
                .then(|| EntryType::Directory)
                .unwrap_or(EntryType::File),
            len_bytes: file_meta.len(),
            modified: file_meta
                .modified()
                .ok()
                .and_then(|time| Zoned::try_from(time).ok())
                .map(|datetime| datetime.strftime("%Y-%m-%d %H:%M:%S").to_string())
                .unwrap_or_else(|| "Unknown".to_string()),
        });
    }
}
