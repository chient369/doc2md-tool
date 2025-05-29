import os
import subprocess
import importlib.util
import sys
import json
import time
from datetime import datetime

def install_package(package_name):
    """Check and install a Python package if it is not already installed."""
    if importlib.util.find_spec(package_name) is None:
        print(f"Installing {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"{package_name} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package_name}: {e}")
            sys.exit(1)
    else:
        print(f"{package_name} is already installed")

def configure_markitdown():
    """Configure MarkItDown with optimized settings."""
    from markitdown import MarkItDown
    md = MarkItDown(
        pdf_ocr=True,  # Enable OCR for PDF files
        excel_table_format="markdown",  # Convert Excel tables to Markdown
        pptx_extract_notes=True,  # Extract notes from PPTX files
        pptx_extract_images=False,  # Do not extract images from PPTX (reduces output size)
        output_encoding="utf-8"  # Ensure UTF-8 encoding
    )
    return md

def load_config(config_path="convert_config.json"):
    """Load configuration from external JSON file."""
    default_config = {
        "file_types": [".pdf", ".xlsx", ".docx", ".pptx"],
        "ignore_patterns": ["*"]
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                print(f"Loaded configuration from {config_path}")
                return config
        except Exception as e:
            print(f"Error loading config file {config_path}: {e}")
            print("Using default configuration instead.")
    else:
        print(f"Config file {config_path} not found. Using default configuration.")
        # Create default config file for future use
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
        print(f"Default configuration saved to {config_path}")
    
    return default_config

def update_cursorignore(project_folder, ignore_patterns, file_types):
    """Update or create .cursorignore to exclude original files and folders containing converted files."""
    cursorignore_path = os.path.join(project_folder, ".cursorignore")
    
    # Add patterns for file types
    patterns_to_add = set()
    
    # Add file types patterns
    for ext in file_types:
        patterns_to_add.add(f"*{ext}")
    
    # Add ignore patterns from config
    for pattern in ignore_patterns:
        patterns_to_add.add(pattern)
    
    # Read existing patterns from .cursorignore (if it exists)
    existing_patterns = set()
    if os.path.exists(cursorignore_path):
        with open(cursorignore_path, "r", encoding="utf-8") as f:
            existing_patterns = {line.strip() for line in f if line.strip()}
    
    # Add new patterns if they don't already exist
    new_patterns = patterns_to_add - existing_patterns
    if new_patterns:
        with open(cursorignore_path, "a", encoding="utf-8") as f:
            for pattern in new_patterns:
                f.write(f"{pattern}\n")
        print(f"Updated .cursorignore with: {new_patterns}")

def convert_files(input_path, output_folder, file_types):
    """Convert files matching specified types directly from input path."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    md = configure_markitdown()
    
    if not os.path.exists(input_path):
        print(f"Directory {input_path} does not exist")
        return []
    
    # Track all converted files for metadata
    converted_files = []
    # Track all folders containing converted files
    converted_folders = set()
    # Track created output directories to avoid redundant checks
    created_output_dirs = set([output_folder])
    
    # Process files recursively through all subfolders
    for root, dirs, files in os.walk(input_path):
        # Get files to convert in this directory
        files_to_convert = [
            filename for filename in files 
            if os.path.splitext(filename)[1].lower() in file_types
        ]
        
        # Skip directory creation if no files to convert
        if not files_to_convert:
            continue
            
        # Create the same folder structure in the output directory only if needed
        relative_path = os.path.relpath(root, input_path)
        output_dir = os.path.join(output_folder, relative_path) if relative_path != '.' else output_folder
        
        # Create output directory if it doesn't exist yet
        if output_dir not in created_output_dirs and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            created_output_dirs.add(output_dir)
        
        # Process only files with specified extensions
        for filename in files_to_convert:
            input_file_path = os.path.join(root, filename)
            # Preserve folder structure in output path
            output_path = os.path.join(output_dir, f"{filename}.md")
            
            try:
                # Skip if file is already converted and unchanged
                if os.path.exists(output_path) and os.path.getmtime(input_file_path) <= os.path.getmtime(output_path):
                    print(f"Skipping {input_file_path}, already converted")
                    converted_files.append(output_path)
                    # Add folder to the set of converted folders
                    converted_folders.add(os.path.dirname(input_file_path))
                    continue
                
                result = md.convert(input_file_path)
                # Replace all NaN values with empty string
                result.text_content = result.text_content.replace('NaN', '')
                
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(result.text_content)
                print(f"Converted {input_file_path} to {output_path}")
                converted_files.append(output_path)
                # Add folder to the set of converted folders
                converted_folders.add(os.path.dirname(input_file_path))
            except Exception as e:
                print(f"Error converting {input_file_path}: {e}")
    
    # Update .cursorignore with folders containing converted files
    if converted_folders:
        cursorignore_path = os.path.join(os.path.dirname(output_folder), ".cursorignore")
        with open(cursorignore_path, "a", encoding="utf-8") as f:
            for folder in converted_folders:
                relative_folder = os.path.relpath(folder, os.path.dirname(cursorignore_path))
                f.write(f"{relative_folder}/*\n")
        print(f"Added {len(converted_folders)} folders to .cursorignore")
    
    return converted_files

def update_metadata_file(project_folder, converted_files):
    """Create or update metadata.md to store metadata of Markdown files in doc_base folder."""
    if not converted_files:
        print("No files were converted, skipping metadata update")
        return
    
    # Đảm bảo thư mục doc_base tồn tại
    doc_base_folder = os.path.join(project_folder, "doc_base")
    if not os.path.exists(doc_base_folder):
        os.makedirs(doc_base_folder)
    
    metadata_file = os.path.join(doc_base_folder, "metadata.md")
    metadata_lines = ["# Metadata of Markdown Files", "", "| Filename | Path | Last Modified |", "|----------|------|---------------|"]
    
    # Process all converted files
    for file_path in converted_files:
        try:
            filename = os.path.basename(file_path)
            last_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M")
            relative_path = os.path.relpath(file_path, project_folder)
            metadata_lines.append(f"| {filename} | {relative_path} | {last_modified} |")
        except Exception as e:
            print(f"Error indexing {file_path}: {e}")
    
    try:
        with open(metadata_file, "w", encoding="utf-8") as f:
            f.write("\n".join(metadata_lines))
        print(f"Metadata file updated: {metadata_file}")
    except Exception as e:
        print(f"Error writing metadata.md: {e}")
        sys.exit(1) 