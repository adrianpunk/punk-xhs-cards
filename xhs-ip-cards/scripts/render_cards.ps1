param(
    [Parameter(Mandatory = $true, Position = 0)] [string] $CardsJson,
    [Parameter(Mandatory = $true, Position = 1)] [string] $OutputDir,
    [Parameter(Mandatory = $true, Position = 2)] [string] $ProfileJson,
    [switch] $AllowDraft,
    [string] $Font,
    [string] $MonoFont
)

$ErrorActionPreference = "Stop"
$Renderer = Join-Path $PSScriptRoot "render_cards.py"
$ExtraArgs = @()
if ($AllowDraft) {
    $ExtraArgs += "--allow-draft"
}
if ($Font) {
    $ExtraArgs += @("--font", $Font)
}
if ($MonoFont) {
    $ExtraArgs += @("--mono-font", $MonoFont)
}

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $Renderer $CardsJson $OutputDir $ProfileJson @ExtraArgs
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    & python3 $Renderer $CardsJson $OutputDir $ProfileJson @ExtraArgs
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $Renderer $CardsJson $OutputDir $ProfileJson @ExtraArgs
} else {
    Write-Error "Python 3 was not found. Install Python 3.10 or later and retry."
    exit 5
}

exit $LASTEXITCODE
