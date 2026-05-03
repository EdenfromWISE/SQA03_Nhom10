param(
    [switch]$NoRollback
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $repoRoot

$reportsRoot = Join-Path $repoRoot "postman\reports"
New-Item -ItemType Directory -Path $reportsRoot -Force | Out-Null

$runId = Get-Date -Format "yyyyMMdd_HHmmss"
$runDir = Join-Path $reportsRoot $runId
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

$collectionPath = Join-Path $repoRoot "postman\E-Vocab-API.postman_collection.json"
$environmentPath = Join-Path $repoRoot "postman\E-Vocab-Local.postman_environment.json"

& (Join-Path $PSScriptRoot "seed_postman_data.ps1")
& (Join-Path $PSScriptRoot "capture_db_snapshot.ps1") -OutputPath (Join-Path $runDir "db_snapshot_pre.json")

Write-Host "Starting Django server for Postman run..."
$server = Start-Process -FilePath "python" -ArgumentList @(
    "manage.py",
    "runserver",
    "127.0.0.1:8000",
    "--settings=core.settings_postman",
    "--noreload"
) -WorkingDirectory $repoRoot -PassThru -WindowStyle Hidden

try {
    $maxAttempts = 30
    $attempt = 0
    $serverReady = $false
    while ($attempt -lt $maxAttempts -and -not $serverReady) {
        $attempt += 1
        Start-Sleep -Seconds 1
        try {
            $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8000/accounts/login/" -Method GET -TimeoutSec 2 -UseBasicParsing
            if ($resp.StatusCode -in @(200, 302)) {
                $serverReady = $true
            }
        } catch {
            # keep waiting
        }
    }

    if (-not $serverReady) {
        throw "Django server was not ready in time."
    }

    Write-Host "Running Newman collection..."
    $newmanExitCode = 0
    try {
        $newmanArgs = @(
            "newman",
            "run",
            $collectionPath,
            "-e",
            $environmentPath,
            "--reporters",
            "cli,json,junit",
            "--reporter-json-export",
            (Join-Path $runDir "newman_report.json"),
            "--reporter-junit-export",
            (Join-Path $runDir "newman_report.xml")
        )
        & npx --yes @newmanArgs
        $newmanExitCode = $LASTEXITCODE
    } catch {
        Write-Host "Newman execution threw an exception:" $_
        $newmanExitCode = 1
    }

    Write-Host "Capturing post-run DB snapshot..."
    & (Join-Path $PSScriptRoot "capture_db_snapshot.ps1") -OutputPath (Join-Path $runDir "db_snapshot_post.json")

    if (-not $NoRollback) {
        Write-Host "Running rollback..."
        & (Join-Path $PSScriptRoot "rollback_postman_data.ps1")
    }

    Write-Host "Capturing post-rollback DB snapshot..."
    & (Join-Path $PSScriptRoot "capture_db_snapshot.ps1") -OutputPath (Join-Path $runDir "db_snapshot_after_rollback.json")

    $summary = [ordered]@{
        run_id = $runId
        collection = $collectionPath
        environment = $environmentPath
        newman_exit_code = $newmanExitCode
        db_snapshot_pre = "db_snapshot_pre.json"
        db_snapshot_post = "db_snapshot_post.json"
        db_snapshot_after_rollback = "db_snapshot_after_rollback.json"
        report_json = "newman_report.json"
        report_junit = "newman_report.xml"
    }

    $reportJsonPath = Join-Path $runDir "newman_report.json"
    if (Test-Path $reportJsonPath) {
        $newmanReport = Get-Content -Raw -Path $reportJsonPath | ConvertFrom-Json
        $summary.total_assertions = $newmanReport.run.stats.assertions.total
        $summary.failed_assertions = $newmanReport.run.stats.assertions.failed
        $summary.total_requests = $newmanReport.run.stats.requests.total
        $summary.failed_requests = $newmanReport.run.failures.Count
    }

    $summaryPath = Join-Path $runDir "summary.json"
    $summary | ConvertTo-Json -Depth 5 | Set-Content -Path $summaryPath -Encoding utf8

    Write-Host "Newman run completed. Artifacts: $runDir"
    if ($newmanExitCode -ne 0) {
        exit $newmanExitCode
    }
} catch {
    Write-Error $_
    exit 1
} finally {
    if ($server -and -not $server.HasExited) {
        Stop-Process -Id $server.Id
    }
}
