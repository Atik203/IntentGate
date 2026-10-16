# Bootstrap data/raw/ to the exact pinned benchmark versions.
# Reads pins from configs/benchmark_versions.yaml (single source of truth), verifies existing
# clones against those pins, and repairs drift by re-fetching the pinned commit shallowly.
#
# Run from repo root:
#   powershell -ExecutionPolicy Bypass -File scripts/clone_benchmarks.ps1
#   powershell -ExecutionPolicy Bypass -File scripts/clone_benchmarks.ps1 -VerifyOnly
#   powershell -ExecutionPolicy Bypass -File scripts/clone_benchmarks.ps1 -Force -Only ToolGate
#
# Flags:
#   -VerifyOnly  Check every clone against its pin; download nothing; exit 1 on drift.
#   -Force       Delete and rebuild the selected targets even when they already match.
#   -Only <name> Operate on a single benchmark (InjecAgent | ToolGate | MCPTox | AgentDojo).
#
# MCPTox has no commit to pin - it is a frozen ZIP snapshot, so integrity is checked by
# verifying the extracted files exist rather than by commit hash.
[CmdletBinding()]
param(
    [switch]$VerifyOnly,
    [switch]$Force,
    [ValidateSet("InjecAgent", "ToolGate", "MCPTox", "AgentDojo")]
    [string]$Only
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Raw = Join-Path $Root "data\raw"
$PinFile = Join-Path $Root "configs\benchmark_versions.yaml"

# yaml section name -> directory name under data/raw
$DirNames = @{
    InjecAgent = "InjecAgent"
    ToolGate   = "ToolGate"
    MCPTox     = "mcptox"
    AgentDojo  = "agentdojo"
}

# Files each target must contain once healthy. Paths are relative to the clone root and are
# the ones the harness actually reads, so a missing entry means a benchmark run would fail.
$Expected = @{
    InjecAgent = @(
        "data/tools.json"
        "data/test_cases_ds_base.json"
        "data/test_cases_dh_base.json"
        "data/test_cases_ds_enhanced.json"
        "data/test_cases_dh_enhanced.json"
        "data/attacker_simulated_responses.json"
    )
    ToolGate  = @("toolgate", "setup.py")
    MCPTox    = @("pure_tool.json", "response_all.json", "def_tool")
    AgentDojo = @("src", "pyproject.toml")
}

function Read-Pins {
    param([string]$Path)
    if (-not (Test-Path $Path)) { throw "pin file not found: $Path" }
    $pins = [ordered]@{}
    $current = $null
    foreach ($line in Get-Content $Path) {
        if ($line -match '^([A-Za-z][A-Za-z0-9]*):\s*$') {
            $current = $Matches[1]
            $pins[$current] = [ordered]@{}
        }
        elseif ($current -and $line -match '^\s{2}([A-Za-z_]+):\s*(.+?)\s*$') {
            $pins[$current][$Matches[1]] = $Matches[2]
        }
    }
    return $pins
}

function Get-Head {
    param([string]$Dir)
    if (-not (Test-Path (Join-Path $Dir ".git"))) { return $null }
    $h = git -C $Dir rev-parse HEAD
    if ($LASTEXITCODE -ne 0) { return $null }
    return "$h".Trim()
}

function Get-MissingFiles {
    param([string]$Dir, [string[]]$Files)
    $missing = @()
    foreach ($f in $Files) {
        if (-not (Test-Path (Join-Path $Dir $f))) { $missing += $f }
    }
    return $missing
}

function Invoke-Checked {
    param([string]$Label, [scriptblock]$Action)
    & $Action | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "$Label failed (git exit $LASTEXITCODE)" }
}

function Set-RepoClone {
    param([string]$Dir, [string]$Url, [string]$Commit)
    if (Test-Path $Dir) { Remove-Item -Recurse -Force $Dir }
    New-Item -ItemType Directory -Force -Path $Dir | Out-Null
    Invoke-Checked "git init in $Dir" { git -C $Dir init -q }
    Invoke-Checked "git remote add" { git -C $Dir remote add origin $Url }
    Invoke-Checked "git fetch $Commit (server may not permit fetch-by-SHA)" {
        git -C $Dir fetch --depth 1 origin $Commit
    }
    Invoke-Checked "git checkout FETCH_HEAD" { git -C $Dir checkout -q FETCH_HEAD }
}

function Set-McptoxSnapshot {
    param([string]$Dir, [string]$ZipUrl)
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("mcptox_" + [Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    try {
        $zip = Join-Path $tmp "mcptox.zip"
        Write-Host "  downloading snapshot..."
        Invoke-WebRequest -Uri $ZipUrl -OutFile $zip -UseBasicParsing
        $extract = Join-Path $tmp "x"
        Expand-Archive -Path $zip -DestinationPath $extract -Force

        $source = $extract
        $children = @(Get-ChildItem -Force $extract)
        if ($children.Count -eq 1 -and $children[0].PSIsContainer) { $source = $children[0].FullName }

        if (Test-Path $Dir) { Remove-Item -Recurse -Force $Dir }
        New-Item -ItemType Directory -Force -Path $Dir | Out-Null
        Get-ChildItem -Force $source | ForEach-Object { Move-Item -Path $_.FullName -Destination $Dir }
    }
    finally {
        if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue }
    }
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "git not found on PATH" }
$pins = Read-Pins -Path $PinFile
$targets = if ($Only) { @($Only) } else { @("InjecAgent", "ToolGate", "MCPTox", "AgentDojo") }

if (-not $VerifyOnly) { New-Item -ItemType Directory -Force -Path $Raw | Out-Null }

$report = @()

foreach ($name in $targets) {
    $pin = $pins[$name]
    if (-not $pin) { throw "no pin entry for '$name' in $PinFile" }

    $dir = Join-Path $Raw $DirNames[$name]
    $files = $Expected[$name]
    $label = if ($name -eq "MCPTox") { "snapshot" } else { "commit" }

    $head = Get-Head -Dir $dir
    $missing = Get-MissingFiles -Dir $dir -Files $files
    $healthy = ($missing.Count -eq 0) -and
               (($name -eq "MCPTox") -or ($head -and $head.StartsWith($pin["commit"])))

    if ($VerifyOnly) {
        if (-not (Test-Path $dir)) {
            $report += [pscustomobject]@{ Name = $name; Status = "MISSING"; Detail = "not cloned" }
            continue
        }
        if ($name -ne "MCPTox" -and $head -and -not $head.StartsWith($pin["commit"])) {
            $report += [pscustomobject]@{
                Name   = $name
                Status = "DRIFT"
                Detail = "HEAD $($head.Substring(0,8)) != pin $($pin['commit'].Substring(0,8))"
            }
            continue
        }
        if ($missing.Count -gt 0) {
            $report += [pscustomobject]@{
                Name   = $name
                Status = "INCOMPLETE"
                Detail = "missing: $($missing -join ', ')"
            }
            continue
        }
        $report += [pscustomobject]@{ Name = $name; Status = "OK"; Detail = "verified" }
        continue
    }

    if ($healthy -and -not $Force) {
        $detail = if ($name -eq "MCPTox") { "already extracted" }
                  else { "HEAD $($head.Substring(0,8)) matches pin" }
        $report += [pscustomobject]@{ Name = $name; Status = "OK"; Detail = $detail }
        continue
    }

    Write-Host "== $name =="
    $action = if ($healthy -and $Force) { "rebuilt" }
              elseif (Test-Path $dir) { "repaired" }
              else { "cloned" }

    try {
        if ($name -eq "MCPTox") {
            Set-McptoxSnapshot -Dir $dir -ZipUrl $pin["snapshot_zip"]
        }
        else {
            Set-RepoClone -Dir $dir -Url $pin["source"] -Commit $pin["commit"]
        }

        $postMissing = Get-MissingFiles -Dir $dir -Files $files
        if ($postMissing.Count -gt 0) {
            throw "still missing after $($action): $($postMissing -join ', ')"
        }

        $head = Get-Head -Dir $dir
        if ($name -ne "MCPTox" -and -not $head.StartsWith($pin["commit"])) {
            throw "HEAD $($head.Substring(0,8)) does not match pin"
        }

        $detail = if ($name -eq "MCPTox") { "snapshot extracted" }
                  else { "HEAD $($head.Substring(0,8)) = pin" }
        $report += [pscustomobject]@{ Name = $name; Status = $action.ToUpper(); Detail = $detail }
    }
    catch {
        $report += [pscustomobject]@{ Name = $name; Status = "FAILED"; Detail = $_.Exception.Message }
    }
}

Write-Host ""
$report | Format-Table -AutoSize | Out-String | Write-Host

$failed = @($report | Where-Object { $_.Status -in @("FAILED", "DRIFT", "INCOMPLETE", "MISSING") })
if ($failed.Count -gt 0) {
    Write-Host "$($failed.Count) target(s) need attention." -ForegroundColor Red
    exit 1
}

if ($VerifyOnly) {
    Write-Host "All $($report.Count) targets match pins in configs/benchmark_versions.yaml." -ForegroundColor Green
}
else {
    Write-Host "data/raw/ ready. Cite these pins in every results log (blueprint Sec 8)." -ForegroundColor Green
}
exit 0
