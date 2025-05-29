#!/bin/bash
#
# SYNOPSIS:
#   Clone/update repository, install doc2md-tool package and configure environment.
#
# USAGE:
#   ./setup_convert.sh <repo_url> <repo_dir>
#   repo_url: URL của repository cần clone (bắt buộc)
#   repo_dir: Thư mục clone về (mặc định: ~/doc2md-tool)

set -e

REPO_URL=${1:-"https://github.com/chient369/doc2md-tool.git"}
REPO_DIR=${2:-"$HOME/doc2md-tool"}

if [ -z "$REPO_URL" ]; then
  echo "Input repo_url"
  echo "Usage: ./setup_convert.sh <repo_url> <repo_dir>"
  exit 1
fi

# Clone hoặc pull repo
if [ ! -d "$REPO_DIR/.git" ]; then
  echo "Cloning repository from $REPO_URL into $REPO_DIR"
  git clone "$REPO_URL" "$REPO_DIR"
else
  echo "Updating repository in $REPO_DIR"
  cd "$REPO_DIR"
  git pull
fi
cd "$REPO_DIR"

# Cài đặt package Python
echo "Installing package..."
pip3 install .

# Thêm Python Scripts vào PATH nếu chưa có
PYTHON_SCRIPTS=$(python3 -c 'import sysconfig; print(sysconfig.get_path("scripts"))')
if [[ ":$PATH:" != *":$PYTHON_SCRIPTS:"* ]]; then
  echo "export PATH=\"$PYTHON_SCRIPTS:\$PATH\"" >> ~/.bashrc
  echo "Added $PYTHON_SCRIPTS to PATH in ~/.bashrc. Restart your terminal or run: source ~/.bashrc"
else
  echo "Python Scripts đã có trong PATH."
fi

echo "Setup complete! You can use the convert-docs command from anywhere." 