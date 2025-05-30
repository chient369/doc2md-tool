import os
import subprocess
import importlib.util
import sys
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Union
import requests

# ----- Package & Dependency Management -----

def install_package(package_name: str, extras: Optional[str] = None) -> None:
    """
    Check and install a Python package if it is not already installed.
    
    Args:
        package_name: Name of the package to install
        extras: Optional extras to include in the installation
    """
    package_spec = package_name
    if extras:
        package_spec = f"{package_name}[{extras}]"
    
    if importlib.util.find_spec(package_name) is None:
        print(f"Installing {package_spec}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_spec])
            print(f"{package_spec} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package_spec}: {e}")
            sys.exit(1)
    else:
        print(f"{package_name} is already installed")
        # Check if we need to upgrade with extras
        if extras:
            print(f"Ensuring {package_name} has all required extras [{extras}]...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package_spec])
                print(f"{package_spec} extras installed/upgraded successfully")
            except subprocess.CalledProcessError as e:
                print(f"Error installing extras for {package_name}: {e}")
                sys.exit(1)

def setup_markitdown() -> None:
    """
    Setup MarkItDown with all required dependencies and update PATH if needed.
    """
    # Install markitdown with all extras
    install_package("markitdown", "all")
    
    # Update PATH to include Python Scripts directory if not already there
    try:
        # Find Python Scripts directory
        python_exe = sys.executable
        python_dir = os.path.dirname(python_exe)
        scripts_dir = os.path.join(python_dir, "Scripts")
        
        if not os.path.exists(scripts_dir):
            # Try alternative location (used in some Python installations)
            scripts_dir = os.path.join(os.path.dirname(python_dir), "Scripts")
        
        if os.path.exists(scripts_dir):
            # Check if scripts_dir is in PATH
            path_env = os.environ.get("PATH", "")
            if scripts_dir not in path_env:
                # Add to current session PATH
                os.environ["PATH"] = f"{scripts_dir}{os.pathsep}{path_env}"
                print(f"Added {scripts_dir} to PATH for current session")
                
                # Check if running on Windows to update PATH permanently
                if sys.platform == "win32":
                    try:
                        # Use subprocess to call PowerShell to update user PATH
                        update_cmd = f'[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + "{os.pathsep}{scripts_dir}", "User")'
                        subprocess.run(["powershell", "-Command", update_cmd], check=True)
                        print(f"Added {scripts_dir} to user PATH permanently")
                    except subprocess.SubprocessError as e:
                        print(f"Warning: Could not update PATH permanently: {e}")
                        print("You may need to manually add the Python Scripts directory to your PATH")
        else:
            print("Warning: Could not find Python Scripts directory")
    except Exception as e:
        print(f"Warning: Could not update PATH: {e}")

def configure_markitdown(config: Optional[Dict[str, Any]] = None) -> Any:
    """
    Configure MarkItDown with optimized settings.
    
    Args:
        config: Optional configuration dictionary containing converter_options
        
    Returns:
        MarkItDown: Configured MarkItDown instance
    """
    # Ensure markitdown is installed with all extras
    setup_markitdown()
    
    # Default settings
    settings = {
        "pdf_ocr": True,
        "excel_table_format": "markdown",
        "pptx_extract_notes": True,
        "pptx_extract_images": False,
        "output_encoding": "utf-8"
    }
    
    # Override with settings from config if provided
    if config and "converter_options" in config:
        settings.update(config["converter_options"])
    
    from markitdown import MarkItDown
    md = MarkItDown(**settings)
    return md

# ----- Configuration Management -----

def load_config(config_path: str = "convert_config.json") -> Dict[str, Any]:
    """
    Load configuration from external JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dict containing configuration settings
    """
    default_config = {
        "file_types": [".pdf", ".xlsx", ".docx", ".pptx", ".xls", ".doc", ".xlsm", ".png", ".jpg", ".jpeg"],
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
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4)
            print(f"Default configuration saved to {config_path}")
        except Exception as e:
            print(f"Error creating default config file: {e}")
    
    return default_config

# ----- Environment & Project Setup -----

def update_cursorignore(project_folder: str, ignore_patterns: List[str], file_types: List[str]) -> None:
    """
    Update or create .cursorignore to exclude original files and folders containing converted files.
    
    Args:
        project_folder: Root folder of the project
        ignore_patterns: Patterns to ignore
        file_types: File extensions to ignore
    """
    cursorignore_path = os.path.join(project_folder, ".cursorignore")
    
    # Add patterns for file types
    patterns_to_add = set()
    
    # Add file types patterns
    for ext in file_types:
        patterns_to_add.add(f"*{ext}")
    
    # Add ignore patterns from config
    for pattern in ignore_patterns:
        # Remove * if present
        clean_pattern = pattern.replace("*", "").replace("/", "\\")
        if clean_pattern:  # Only add non-empty patterns
            patterns_to_add.add(clean_pattern)
    
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
        print(f"Updated .cursorignore with: {', '.join(new_patterns)}")

    # Update .cursorignore with folders containing converted files (use \\)
    folder_patterns = set()
    if os.path.exists(cursorignore_path):
        with open(cursorignore_path, "r", encoding="utf-8") as f:
            for line in f:
                l = line.strip()
                if l.endswith("\\"):
                    folder_patterns.add(l)
    
    # Get list of folders from recent conversions (if any)
    if hasattr(update_cursorignore, "converted_folders"):
        for folder in update_cursorignore.converted_folders:
            rel_folder = os.path.relpath(folder, project_folder).replace("/", "\\")
            if not rel_folder.endswith("\\"):
                rel_folder += "\\"
            if rel_folder not in folder_patterns:
                with open(cursorignore_path, "a", encoding="utf-8") as f:
                    f.write(f"{rel_folder}\n")
                folder_patterns.add(rel_folder)
        print(f"Added {len(folder_patterns)} folders to .cursorignore")
    # Remove attribute after use
    if hasattr(update_cursorignore, "converted_folders"):
        del update_cursorignore.converted_folders

def update_vscode_settings(output_folder: str) -> None:
    """
    Update VS Code settings to exclude the output folder.
    
    Args:
        output_folder: Path to the output folder
    """
    vscode_settings_path = os.path.join(os.getcwd(), '.vscode', 'settings.json')
    
    # Ensure .vscode directory exists
    if not os.path.exists(os.path.dirname(vscode_settings_path)):
        os.makedirs(os.path.dirname(vscode_settings_path))
    
    # Load existing settings or create new
    settings = {}
    if os.path.exists(vscode_settings_path):
        try:
            with open(vscode_settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except json.JSONDecodeError:
            print("Warning: Invalid VS Code settings file. Creating a new one.")
    
    # Update files.exclude
    files_exclude = settings.get('files.exclude', {})
    relative_output_folder = os.path.relpath(output_folder, os.getcwd()).replace("\\", "/")
    files_exclude[relative_output_folder] = True
    settings['files.exclude'] = files_exclude
    
    # Write back to settings.json
    try:
        with open(vscode_settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
        print(f"Updated VS Code settings to exclude {relative_output_folder}")
    except Exception as e:
        print(f"Error updating VS Code settings: {e}")

def update_gitignore(output_folder: str) -> None:
    """
    Add the output folder to .gitignore.
    
    Args:
        output_folder: Path to the output folder
    """
    gitignore_path = os.path.join(os.getcwd(), '.gitignore')
    
    # Read existing .gitignore patterns
    existing_patterns = set()
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            existing_patterns = {line.strip() for line in f if line.strip()}
    
    # Add output folder if not already present
    relative_output_folder = os.path.relpath(output_folder, os.getcwd()).replace("\\", "/")
    if relative_output_folder not in existing_patterns:
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            f.write(f"{relative_output_folder}/\n")
        print(f"Added {relative_output_folder} to .gitignore")

def add_cursor_rules_from_docs() -> None:
    """
    Add cursor rules from docs-search-standard.md in installed package to the current user's directory.
    """
    # Find the installed package directory (e.g. doc2md_tool)
    try:
        spec = importlib.util.find_spec("doc2md_tool")
        if spec is None or not spec.submodule_search_locations:
            # Try local cursor_rules directory instead
            current_dir = os.getcwd()
            local_rules_path = os.path.join(current_dir, 'cursor_rules', 'docs-search-standard.md')
            if os.path.exists(local_rules_path):
                docs_path = local_rules_path
            else:
                print("Can't find the installed package doc2md_tool or local rules.")
                return
        else:
            package_dir = spec.submodule_search_locations[0]
            docs_path = os.path.join(package_dir, 'cursor_rules', 'docs-search-standard.md')
    except Exception as e:
        print(f"Can't find the installed package directory: {e}")
        return
    
    # Ensure the cursor rules directory exists
    rules_dir = os.path.join(os.getcwd(), '.cursor', 'rules')
    os.makedirs(rules_dir, exist_ok=True)
    rules_path = os.path.join(rules_dir, 'docs-search-standard.mdc')
    
    # Ensure the source file exists
    if not os.path.exists(docs_path):
        print(f"Source file {docs_path} does not exist.")
        return
    
    # Read content from docs-search-standard.md
    try:
        with open(docs_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {docs_path}: {e}")
        return
    
    # Write content to cursor_rules.md in the current directory
    try:
        with open(rules_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Cursor rules added to {rules_path}")
    except Exception as e:
        print(f"Error writing to {rules_path}: {e}")

# ----- Version Management -----

def get_latest_github_version(repo: str) -> Optional[str]:
    """
    Get the latest tag version from a GitHub repo.
    
    Args:
        repo: GitHub repository in the format "username/repo"
        
    Returns:
        Latest version tag or None if unavailable
    """
    url = f"https://api.github.com/repos/{repo}/tags"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            tags = response.json()
            if tags:
                return tags[0]['name']  # Latest tag
        print("Can't get the latest version from GitHub.")
    except Exception as e:
        print(f"Error when querying GitHub: {e}")
    return None

def get_local_version_from_setup() -> Optional[str]:
    """
    Get the current version from setup.py.
    
    Returns:
        Current version or None if unavailable
    """
    try:
        if not os.path.exists('setup.py'):
            print("setup.py file not found.")
            return None
            
        with open('setup.py', 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Can't get the local version: {e}")
    return None

def check_and_upgrade_github_repo() -> None:
    """
    Check the latest version on GitHub and upgrade if needed.
    """
    repo = "chient369/doc2md-tool"
    local_version = get_local_version_from_setup()
    github_version = get_latest_github_version(repo)
    
    if local_version and github_version:
        if local_version != github_version:
            print(f"Upgrading doc2md-tool from {local_version} to {github_version} (GitHub)...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", f"git+https://github.com/{repo}.git"])
                print(f"Upgraded doc2md-tool to {github_version}")
            except subprocess.CalledProcessError as e:
                print(f"Error upgrading doc2md-tool: {e}")
        else:
            print(f"doc2md-tool is the latest version ({local_version})")
    else:
        print("Can't check the local version or GitHub.")

# ----- File Conversion -----

def convert_files(input_path: str, output_folder: str, file_types: List[str], config: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    Convert files matching specified types directly from input path.
    
    Args:
        input_path: Directory containing files to convert
        output_folder: Directory for converted Markdown files
        file_types: List of file extensions to convert
        config: Optional configuration dictionary
        
    Returns:
        List of paths to converted files
    """
    # Check and upgrade markitdown and main repo if needed
    install_package("markitdown", "all")
    check_and_upgrade_github_repo()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Update VS Code settings and .gitignore
    update_vscode_settings(output_folder)
    update_gitignore(output_folder)
    
    # Add cursor rules
    add_cursor_rules_from_docs()
    
    # Configure MarkItDown with settings from config
    md = configure_markitdown(config)
    
    if not os.path.exists(input_path):
        print(f"Directory {input_path} does not exist")
        return []
    
    # Track all converted files for metadata
    converted_files: List[str] = []
    # Track all folders containing converted files
    converted_folders: Set[str] = set()
    # Track created output directories to avoid redundant checks
    created_output_dirs: Set[str] = set([output_folder])
    
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
                
                # Convert file to Markdown
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
    
    # Store converted folders for updating .cursorignore
    update_cursorignore.converted_folders = converted_folders
    
    # Return list of converted files
    return converted_files

# ----- Metadata Management -----

def update_metadata_file(project_folder: str, converted_files: List[str]) -> None:
    """
    Create or update metadata.md to store metadata of Markdown files in doc_base folder.
    
    Args:
        project_folder: Root folder of the project
        converted_files: List of paths to converted files
    """
    if not converted_files:
        print("No files were converted, skipping metadata update")
        return
    
    # Ensure doc_base directory exists
    doc_base_folder = os.path.join(project_folder, "doc_base")
    if not os.path.exists(doc_base_folder):
        os.makedirs(doc_base_folder)
    
    metadata_file = os.path.join(doc_base_folder, "metadata.md")
    metadata_lines = [
        "# Metadata of Markdown Files", 
        "", 
        "| Filename | Path | Last Modified |", 
        "|----------|------|---------------|"
    ]
    
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