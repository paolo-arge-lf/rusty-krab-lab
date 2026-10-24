//https://www.youtube.com/watch?v=5UA9UWWAagc&t=6s
use clap::Parser;
use owo_colors::OwoColorize;
use std::{
    fs,
    path::{Path, PathBuf},
};

#[derive(Debug, Parser)]
#[command(
    author,
    version,
    about,
    long_about = "CLI tool to manage Linux Fedora Workstation Configuration."
)]
struct Cli {
    path: Option<PathBuf>,
}

fn main() {
    let cli = Cli::parse();
    let path = cli.path.unwrap_or_else(|| PathBuf::from("."));

    if let Ok(does_exist) = fs::exists(&path) {
        if does_exist {
            for file in get_files(&path) {
                println!("{}", file.green());
            }
        } else {
            println!("Path does not exist: {}", path.display().red());
        }
    } else {
        println!("Failed to check if path exists: {}", path.display().red());
    }
}

fn get_files(path: &Path) -> Vec<String> {
    let mut files = Vec::default();
    match fs::read_dir(path) {
        Ok(entries) => {
            for entry in entries {
                if let Ok(dir_entry) = entry {
                    if let Ok(file_type) = dir_entry.file_type() {
                        if file_type.is_file() {
                            files.push(dir_entry.file_name().to_string_lossy().to_string());
                        }
                    }
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
