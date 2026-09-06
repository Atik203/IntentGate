# Clone benchmarks into data/raw (Week 1; blueprint README Quick Start).
# Run from repo root:  powershell -ExecutionPolicy Bypass -File scripts/clone_benchmarks.ps1
$ErrorActionPreference = "Stop"
$dest = "data\raw"
New-Item -ItemType Directory -Force -Path $dest | Out-Null

Write-Host "== InjecAgent =="
if (-not (Test-Path "$dest\InjecAgent")) { git clone --depth 1 https://github.com/uiuc-kang-lab/InjecAgent "$dest\InjecAgent" }
Write-Host "== MCPTox snapshot =="
if (-not (Test-Path "$dest\mcptox")) { git clone --depth 1 https://anonymous.4open.science/r/AAAI26-7C02 "$dest\mcptox" }
Write-Host "== ToolGate (B2 reference) =="
if (-not (Test-Path "$dest\ToolGate")) { git clone --depth 1 https://github.com/OceannTwT/ToolGate "$dest\ToolGate" }
Write-Host "== AgentDojo (stretch) =="
if (-not (Test-Path "$dest\agentdojo")) { git clone --depth 1 https://github.com/ethz-spylab/agentdojo "$dest\agentdojo" }
Write-Host "done. Document exact commit hashes in results logs (blueprint Sec 8)."
