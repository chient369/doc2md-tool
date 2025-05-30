<#
.SYNOPSIS
    Clone/update repository, install SDIMS Converter and configure environment.
.PARAMETER RepoUrl
    URL of the repository to clone or update.
.PARAMETER RepoDir
    Directory to clone or update the repository in (default: C:\doc2md-tool).
#>
param(
    [string]$RepoUrl = "https://github.com/chient369/doc2md-tool.git",
    [string]$RepoDir = "C:\doc2md-tool"
)

# Allow script execution
Write-Host "Setting execution policy to RemoteSigned for current user"
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force

# Function to check if Python is installed and in PATH
function Check-Python {
    # Try multiple possible Python commands
    foreach ($cmd in @('python', 'py')) {
        try {
            $pythonVersion = & $cmd --version 2>&1
            if ($pythonVersion -match "Python (\d+\.\d+\.\d+)") {
                Write-Host "Python is installed: $pythonVersion (using $cmd command)"
                return $true
            }
        } catch {
            # Continue to next command if this one fails
            continue
        }
    }
    return $false
}

# Function to check if pip is available
function Check-Pip {
    try {
        $pipVersion = & pip --version 2>&1
        if ($pipVersion -match "pip (\d+\.\d+)") {
            Write-Host "Pip is installed: $pipVersion"
            return $true
        }
        return $false
    } catch {
        return $false
    }
}

# Check if Python is installed
$pythonInstalled = Check-Python
if (-not $pythonInstalled) {
    Write-Host "Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    exit 1
}

# Check if pip is available
$pipAvailable = Check-Pip
if (-not $pipAvailable) {
    Write-Host "pip is not available in PATH!" -ForegroundColor Red
    Write-Host "Please ensure pip is installed with Python." -ForegroundColor Yellow
    Write-Host "You can try to install it with: python -m ensurepip --upgrade" -ForegroundColor Yellow
    exit 1
}

# Clone or update repository if URL provided, otherwise use script directory
if ($RepoUrl -and $RepoUrl.Trim() -ne "") {
    if (!(Test-Path $RepoDir) -or !(Test-Path (Join-Path $RepoDir ".git"))) {
        Write-Host "Cloning repository from $RepoUrl into $RepoDir"
        git clone $RepoUrl $RepoDir
    } else {
        Write-Host "Updating repository in $RepoDir"
        Push-Location $RepoDir
        git pull
        Pop-Location
    }
    Set-Location $RepoDir
} else {
    # Navigate to script directory
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
    $parentDir = Split-Path -Parent $scriptDir
    Set-Location $parentDir
    Write-Host "Working directory set to: $parentDir"
}

# Install SDIMS Converter package
Write-Host "Installing Converter package..."
try {
    & pip install .
    if ($LASTEXITCODE -ne 0) {
        throw "pip installation failed with exit code $LASTEXITCODE"
    }
} catch {
    Write-Host "Error installing package: $_" -ForegroundColor Red
    exit 1
}

# Add Python Scripts folder to user PATH if not already present
try {
    $pythonExe = (Get-Command python -ErrorAction Stop).Source
    $pythonDir = Split-Path $pythonExe -Parent
    $scriptsDir = Join-Path $pythonDir "Scripts"
    
    if (!(Test-Path $scriptsDir)) {
        Write-Host "Python Scripts directory not found at $scriptsDir" -ForegroundColor Yellow
        # Try another common location
        $scriptsDir = Join-Path (Split-Path $pythonDir -Parent) "Scripts"
        if (!(Test-Path $scriptsDir)) {
            Write-Host "Could not locate Python Scripts directory" -ForegroundColor Red
            $scriptsDir = $null
        }
    }
    
    if ($scriptsDir) {
        $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
        if ($userPath -notlike "*$scriptsDir*") {
            Write-Host "Adding $scriptsDir to user PATH"
            [Environment]::SetEnvironmentVariable("Path", "$userPath;$scriptsDir", "User")
            Write-Host "PATH updated. You'll need to restart your shell for the changes to take effect." -ForegroundColor Green
        } else {
            Write-Host "Scripts directory already in PATH"
        }
    }
} catch {
    Write-Host "Warning: Could not update PATH automatically: $_" -ForegroundColor Yellow
    Write-Host "You may need to manually add your Python Scripts directory to PATH" -ForegroundColor Yellow
}

# Final message
Write-Host "Setup complete. If PATH was updated, restart your shell to apply changes." -ForegroundColor Green
Write-Host "You can then use 'convert-docs' command from anywhere." -ForegroundColor Green 