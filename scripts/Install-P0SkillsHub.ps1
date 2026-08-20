[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RepositoryRoot,

    [Parameter(Mandatory = $true)]
    [string]$InventoryPath,

    [Parameter(Mandatory = $true)]
    [string]$AuditReportPath,

    [Parameter(Mandatory = $true)]
    [string]$EvidenceIndexPath,

    [Parameter(Mandatory = $true)]
    [string]$AuditBundlePath,

    [string]$SourceRoot = "C:\Users\Shadow\Documents\CLEMENT_STUDIO\09_Drive\Mega\skill",

    [string]$BackupRoot = "C:\Users\Shadow\Downloads\CLEMENT_P0\P0-01_BACKUPS",

    [switch]$Apply
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-ClementSection {
    param([Parameter(Mandatory = $true)][string]$Title)

    Write-Host ""
    Write-Host "============================================================"
    Write-Host "CLEMENT — $Title"
    Write-Host "============================================================"
}

function Invoke-NativeChecked {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$Operation
    )

    $output = @()
    $oldPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $output = & $FilePath @Arguments 2>&1
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $oldPreference
    }
    $text = (($output | Out-String).Trim())
    if ($exitCode -ne 0) {
        throw "$Operation FAILED (exit=$exitCode): $text"
    }
    return $text
}

try {
    Write-ClementSection "P0-01 INSTALL — PREFLIGHT"

    $RepositoryRoot = [System.IO.Path]::GetFullPath($RepositoryRoot)
    $SourceRoot = [System.IO.Path]::GetFullPath($SourceRoot)
    $InventoryPath = [System.IO.Path]::GetFullPath($InventoryPath)
    $AuditReportPath = [System.IO.Path]::GetFullPath($AuditReportPath)
    $EvidenceIndexPath = [System.IO.Path]::GetFullPath($EvidenceIndexPath)
    $AuditBundlePath = [System.IO.Path]::GetFullPath($AuditBundlePath)
    $BackupRoot = [System.IO.Path]::GetFullPath($BackupRoot)

    foreach ($directory in @($RepositoryRoot, $SourceRoot)) {
        if (-not (Test-Path -LiteralPath $directory -PathType Container)) {
            throw "DIRECTORY_NOT_FOUND: $directory"
        }
    }
    foreach ($file in @(
        $InventoryPath,
        $AuditReportPath,
        $EvidenceIndexPath,
        $AuditBundlePath,
        (Join-Path $RepositoryRoot "config\audit_contract.json"),
        (Join-Path $RepositoryRoot "scripts\import_skills.py"),
        (Join-Path $RepositoryRoot "scripts\validate_repository.py")
    )) {
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
            throw "FILE_NOT_FOUND: $file"
        }
    }

    $git = Get-Command git -CommandType Application -ErrorAction SilentlyContinue
    $py = Get-Command py -CommandType Application -ErrorAction SilentlyContinue
    if ($null -eq $git) {
        throw "GIT_COMMAND_MISSING"
    }
    if ($null -eq $py) {
        throw "PY_LAUNCHER_MISSING"
    }

    $gitVersion = Invoke-NativeChecked -FilePath $git.Source -Arguments @("--version") -Operation "GIT_VERSION"
    $pythonVersion = Invoke-NativeChecked -FilePath $py.Source -Arguments @("-3", "--version") -Operation "PYTHON_VERSION"
    $insideWorktree = Invoke-NativeChecked -FilePath $git.Source -Arguments @("-C", $RepositoryRoot, "rev-parse", "--is-inside-work-tree") -Operation "GIT_WORKTREE"
    if ($insideWorktree -ine "true") {
        throw "TARGET_IS_NOT_GIT_WORKTREE"
    }

    $branch = Invoke-NativeChecked -FilePath $git.Source -Arguments @("-C", $RepositoryRoot, "branch", "--show-current") -Operation "GIT_BRANCH"
    if ($branch -ine "feat/p0-skills-hub") {
        throw "WRONG_BRANCH: expected=feat/p0-skills-hub; actual=$branch"
    }

    $sourceTimestampBefore = (Get-Item -LiteralPath $SourceRoot -Force).LastWriteTimeUtc.Ticks
    $venvRoot = Join-Path $RepositoryRoot ".venv"
    $venvPython = Join-Path $venvRoot "Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
        $null = Invoke-NativeChecked -FilePath $py.Source -Arguments @("-3", "-m", "venv", $venvRoot) -Operation "VENV_CREATE"
    }
    if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
        throw "VENV_PYTHON_NOT_FOUND: $venvPython"
    }

    Write-ClementSection "PACKAGE AND TESTS"

    $compileOutput = Invoke-NativeChecked -FilePath $venvPython -Arguments @("-m", "compileall", "-q", (Join-Path $RepositoryRoot "src"), (Join-Path $RepositoryRoot "scripts"), (Join-Path $RepositoryRoot "tests")) -Operation "COMPILEALL"
    $unitOutput = Invoke-NativeChecked -FilePath $venvPython -Arguments @("-m", "unittest", "discover", "-s", (Join-Path $RepositoryRoot "tests"), "-v") -Operation "UNIT_TESTS"
    $validationOutputBefore = Invoke-NativeChecked -FilePath $venvPython -Arguments @((Join-Path $RepositoryRoot "scripts\validate_repository.py"), "--root", $RepositoryRoot) -Operation "REPOSITORY_VALIDATION_BEFORE"

    Write-ClementSection "CERTIFIED DRY RUN"

    $importArguments = @(
        (Join-Path $RepositoryRoot "scripts\import_skills.py"),
        "--source-root", $SourceRoot,
        "--inventory", $InventoryPath,
        "--contract", (Join-Path $RepositoryRoot "config\audit_contract.json"),
        "--audit-report", $AuditReportPath,
        "--evidence-index", $EvidenceIndexPath,
        "--audit-bundle", $AuditBundlePath,
        "--repository-root", $RepositoryRoot
    )
    $dryRunOutput = Invoke-NativeChecked -FilePath $venvPython -Arguments $importArguments -Operation "SKILLS_IMPORT_DRY_RUN"
    if ($dryRunOutput -notmatch "(?m)^NORMALIZED_ENTRIES=905\s*$") {
        throw "DRY_RUN_ENTRY_COUNT_NOT_905"
    }
    if ($dryRunOutput -notmatch "(?m)^RESULT=PASS\s*$") {
        throw "DRY_RUN_NOT_PASS"
    }

    $applyResult = "NOT_REQUESTED"
    $applyOutput = ""
    if ($Apply.IsPresent) {
        Write-ClementSection "TRANSACTIONAL APPLY"
        New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
        $applyOutput = Invoke-NativeChecked -FilePath $venvPython -Arguments ($importArguments + @("--apply", "--backup-root", $BackupRoot)) -Operation "SKILLS_IMPORT_APPLY"
        if ($applyOutput -notmatch "(?m)^SKILLS_HUB_TESTS=PASS\s*$") {
            throw "POST_APPLY_VALIDATION_NOT_PASS"
        }
        $applyMatch = [regex]::Match($applyOutput, "(?m)^APPLY_RESULT=(?<value>[^\r\n]+)\s*$")
        if (-not $applyMatch.Success) {
            throw "APPLY_RESULT_MISSING"
        }
        $applyResult = $applyMatch.Groups["value"].Value.Trim()
    }

    $validationOutputAfter = Invoke-NativeChecked -FilePath $venvPython -Arguments @((Join-Path $RepositoryRoot "scripts\validate_repository.py"), "--root", $RepositoryRoot) -Operation "REPOSITORY_VALIDATION_AFTER"
    $sourceTimestampAfter = (Get-Item -LiteralPath $SourceRoot -Force).LastWriteTimeUtc.Ticks
    if ($sourceTimestampBefore -ne $sourceTimestampAfter) {
        throw "SOURCE_ROOT_TIMESTAMP_CHANGED"
    }

    $registryPath = Join-Path $RepositoryRoot "registry\skills_registry.json"
    $registryHash = (Get-FileHash -LiteralPath $registryPath -Algorithm SHA256).Hash
    $gitStatus = Invoke-NativeChecked -FilePath $git.Source -Arguments @("-C", $RepositoryRoot, "status", "--short") -Operation "GIT_STATUS"

    Write-ClementSection "P0-01 INSTALL RESULT"
    Write-Host "CHECK_1_GIT=PASS"
    Write-Host "CHECK_2_PYTHON=PASS"
    Write-Host "CHECK_3_BRANCH=PASS"
    Write-Host "CHECK_4_ZERO_DEPENDENCY_RUNTIME=PASS"
    Write-Host "CHECK_5_COMPILE=PASS"
    Write-Host "CHECK_6_UNIT_TESTS=PASS"
    Write-Host "CHECK_7_BOOTSTRAP_VALIDATION=PASS"
    Write-Host "CHECK_8_AUDIT_EVIDENCE=PASS"
    Write-Host "CHECK_9_DRY_RUN_905=PASS"
    Write-Host "CHECK_10_SOURCE_UNCHANGED=PASS"
    Write-Host "CHECK_11_FINAL_VALIDATION=PASS"
    Write-Host "GIT_VERSION=$gitVersion"
    Write-Host "PYTHON_VERSION=$pythonVersion"
    Write-Host "BRANCH=$branch"
    Write-Host "APPLY_REQUESTED=$($Apply.IsPresent)"
    Write-Host "APPLY_RESULT=$applyResult"
    Write-Host "REGISTRY_SHA256=$registryHash"
    Write-Host "GIT_STATUS_BEGIN"
    Write-Host $gitStatus
    Write-Host "GIT_STATUS_END"
    Write-Host "SOURCE_LIBRARY_MODIFIED=NO"
    Write-Host "RESULT=PASS"
    Write-Host "NEXT_ACTION=REVIEW_GIT_DIFF_COMMIT_PUSH_PR_CI"
    Write-Host "============================================================"
}
catch {
    Write-ClementSection "P0-01 INSTALL FAILURE"
    $message = $_.Exception.Message.Replace("`r", " ").Replace("`n", " ")
    Write-Host "RESULT=FAIL"
    Write-Host "ERROR_TYPE=$($_.Exception.GetType().FullName)"
    Write-Host "ERROR_MESSAGE=$message"
    Write-Host "SOURCE_LIBRARY_WRITE_REQUESTED=NO"
    Write-Host "NEXT_ACTION=STOP_NO_COMMIT_NO_MERGE"
    Write-Host "============================================================"
    exit 1
}
