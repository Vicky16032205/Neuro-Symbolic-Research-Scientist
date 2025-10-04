<#
Simple PowerShell helper to start the four FastAPI services as background jobs for local development.
Run this from the repository root in PowerShell (use an elevated terminal if needed).

This script starts each uvicorn server in a background job and prints how to start the Streamlit dashboard.

Note: The background jobs will inherit your current Python/virtualenv PATH. Make sure you've activated your environment first.
#>

param(
    [switch]$SkipUvicorn
)

function Start-ServiceJob($name, $path, $module, $port) {
    $script = "cd $path; uvicorn $module:app --host 127.0.0.1 --port $port --reload"
    Write-Host "Starting $name -> $script"
    Start-Job -Name $name -ScriptBlock { param($s) powershell -NoProfile -Command $s } -ArgumentList $script | Out-Null
}

if (-not $SkipUvicorn) {
    Start-ServiceJob "ingest_search" "$(Resolve-Path .\person_A\ingest_search)" "main" 8000
    Start-ServiceJob "hypothesis_gen" "$(Resolve-Path .\person_A\hypothesis_gen)" "main" 8001
    Start-ServiceJob "z3_validator" "$(Resolve-Path .\person_B\z3_validator)" "main" 8002
    Start-ServiceJob "experiment_design" "$(Resolve-Path .\person_B\experiment_design)" "main" 8003
}

Write-Host "\nFastAPI services started as background jobs (use Get-Job to inspect)."
Write-Host "To view job list: Get-Job | Format-Table -Auto"
Write-Host "To stop jobs: Get-Job | Stop-Job; Get-Job | Remove-Job"

Write-Host "\nStart the dashboard (in a separate terminal) with:"
Write-Host "cd person_B/dashboard; streamlit run app.py"

Write-Host "\nIf you prefer to start services in the foreground instead of background jobs, run the uvicorn commands shown in README.md in separate terminals."
