#!/usr/bin/env python
import os
import sys
import argparse
from typing import NamedTuple, List, Optional
from convert_utils import (
    install_package,
    setup_markitdown,
    load_config,
    update_cursorignore,
    convert_files,
    update_metadata_file
)

class CliArgs(NamedTuple):
    """Class to hold parsed command line arguments."""
    input: str
    output: str
    config: str
    setup_only: bool

def parse_arguments() -> CliArgs:
    """
    Parse command line arguments.
    
    Returns:
        CliArgs object containing parsed arguments
    """
    parser = argparse.ArgumentParser(description="Convert document files to Markdown.")
    parser.add_argument("--input", "-i", default=os.getcwd(),
                      help="Input directory containing files to convert (default: current directory)")
    parser.add_argument("--output", "-o", default="doc_base",
                      help="Output directory for converted Markdown files (default: doc_base)")
    parser.add_argument("--config", "-c", default="convert_config.json",
                      help="Path to configuration file (default: convert_config.json)")
    parser.add_argument("--setup-only", action="store_true",
                      help="Only setup MarkItDown and dependencies without converting files")
    
    args = parser.parse_args()
    return CliArgs(
        input=args.input,
        output=args.output,
        config=args.config,
        setup_only=args.setup_only
    )

def main() -> None:
    """
    Main entry point for the command line interface.
    """
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Setup MarkItDown with all dependencies
        setup_markitdown()
        
        # If only setup was requested, exit
        if args.setup_only:
            print("MarkItDown setup completed. Use 'cvmd' command to convert files.")
            return
        
        # Load configuration from file
        config = load_config(args.config)
        file_types = config.get("file_types", [".pdf", ".xlsx", ".docx", ".pptx", ".xls", ".doc", ".xlsm", ".png", ".jpg", ".jpeg"])
        ignore_patterns = config.get("ignore_patterns", ["*"])
        
        # Configure directories
        input_path = os.path.abspath(args.input)
        project_folder = os.getcwd()  # Use current working directory for metadata
        output_folder = os.path.join(project_folder, args.output)
        
        print(f"Converting files from: {input_path}")
        print(f"Output directory: {output_folder}")
        print(f"File types to convert: {', '.join(file_types)}")
        
        # Update .cursorignore to exclude original files
        update_cursorignore(project_folder, ignore_patterns, file_types)
        
        # Convert files directly from input path
        converted_files = convert_files(input_path, output_folder, file_types, config)
        
        # Update metadata file
        if converted_files:
            update_metadata_file(project_folder, converted_files)
            print(f"Successfully converted {len(converted_files)} files")
        else:
            print(f"No matching files found in {input_path}")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 