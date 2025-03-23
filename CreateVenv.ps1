$CurrentFolder = Get-Location | Split-Path -Leaf
$EnvFolder = "$CurrentFolder-venv"
Write-Output "Using virtual environment directory: [$EnvFolder]"

if (Test-Path $EnvFolder -PathType Container) {
    Write-Output "Virtual environment already exists. Activating virtual environment..."
    Invoke-Expression "./$EnvFolder/Scripts/Activate.ps1"
} else {
    Write-Output "Virtual environment not found. Creating virtual environment and installing dependencies..."

    python -m venv $EnvFolder `
        && Invoke-Expression "./$EnvFolder/Scripts/Activate.ps1" `
        && pip install -r requirements.txt
}