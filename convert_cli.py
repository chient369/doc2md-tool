#!/usr/bin/env python
import os
import sys
import argparse
from convert_utils import (
    install_package,
    load_config,
    update_cursorignore,
    convert_files,
    update_metadata_file
)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert document files to Markdown.")
    parser.add_argument("--input", "-i", default=os.getcwd(),
                      help="Input directory containing files to convert (default: current directory)")
    parser.add_argument("--output", "-o", default="doc_base",
                      help="Output directory for converted Markdown files (default: doc_base)")
    parser.add_argument("--config", "-c", default="convert_config.json",
                      help="Path to configuration file (default: convert_config.json)")
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Install required packages
    install_package("markitdown")
    
    # Load configuration from file
    config = load_config(args.config)
    file_types = config.get("file_types", [".pdf", ".xlsx", ".docx", ".pptx"])
    ignore_patterns = config.get("ignore_patterns", ["*"])
    
    # Configure directories
    input_path = args.input
    project_folder = os.getcwd()  # Use current working directory for metadata
    output_folder = os.path.join(project_folder, args.output)
    
    print(f"Converting files from: {input_path}")
    print(f"Output directory: {output_folder}")
    print(f"File types to convert: {', '.join(file_types)}")
    
    # Update .cursorignore to exclude original files
    update_cursorignore(project_folder, ignore_patterns, file_types)
    
    # Convert files directly from input path
    converted_files = convert_files(input_path, output_folder, file_types)
    
    # Update metadata file
    if converted_files:
        update_metadata_file(output_folder, converted_files)
        print(f"Successfully converted {len(converted_files)} files")
    else:
        print(f"No matching files found in {input_path}")

if __name__ == "__main__":
    main() 