//https://www.youtube.com/watch?v=5UA9UWWAagc&t=6s
use clap::Parser;
use jiff::DateTime;
use owo_colors::OwoColorize;
use std::{
    fs,
    path::{Path, PathBuf},
};
use strum::Display;

#[derive(Debug, Display)]
enum EntryType {
    File,
    Directory,
}

#[derive(Debug)]
struct FileEntry {
    name: String,
    entry_type: EntryType,
    len_bytes: u64,
    modified: String,
}

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
                println!("{}", file.name.green());
            }
        } else {
            println!("Path does not exist: {}", path.display().red());
        }
    } else {
        println!("Failed to check if path exists: {}", path.display().red());
    }
}

fn get_files(path: &Path) -> Vec<FileEntry> {
    let mut files = Vec::default();
    match fs::read_dir(path) {
        Ok(entries) => {
            for entry in entries {
                if let Ok(dir_entry) = entry {
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
                                .map(|time| {
                                    let datetime: jiff::DateTime<jiff::Local> = time.into();
                                    datetime.format("%Y-%m-%d %H:%M:%S").to_string()
                                })
                                .unwrap_or_else(|_| "Unknown".to_string()),
                        });
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
