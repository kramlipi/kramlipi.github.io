# Pull published GHCR image (if needed), mount host folders at the same paths,
# pass host API keys, launch Chat UI.
#
# Usage:
#   .\scripts\docker-ui.ps1
#   $env:WORKSPACE = "D:\path\to\repo"; .\scripts\docker-ui.ps1
#   $env:HOST_ROOT = $env:USERPROFILE; .\scripts\docker-ui.ps1

param(
    [string]$Workspace = $env:WORKSPACE,
    [string]$HostRoot = $(if ($env:HOST_ROOT) { $env:HOST_ROOT } else { $env:USERPROFILE }),
    [string]$Port = $(if ($env:PORT) { $env:PORT } else { "8080" }),
    [string]$Image = $(if ($env:IMAGE) { $env:IMAGE } else { "ghcr.io/kramlipi/code-agent:latest" }),
    [switch]$NoPull
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

if (-not $Workspace) {
    $Workspace = (Get-Location).Path
}
$Workspace = (Resolve-Path $Workspace).Path
if (-not $HostRoot) {
    $HostRoot = $env:USERPROFILE
}
$HostRoot = (Resolve-Path $HostRoot).Path

$sync = Join-Path $PSScriptRoot "sync_host_env.ps1"
if (Test-Path $sync) {
    try { & $sync } catch { Write-Host "sync_host_env skipped: $_" }
}

$hostVars = @(
    "GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
    "DEEPSEEK_API_KEY", "CODE_AGENT_MODEL", "CODE_AGENT_API_BASE", "CODE_AGENT_API_KEY",
    "CODE_AGENT_LOG_LEVEL", "GH_TOKEN", "GITHUB_TOKEN"
)

$envArgs = @(
    "-e", "CODE_AGENT_WORKSPACE=$Workspace",
    "-e", "HOME=$HostRoot",
    "-e", "CODE_AGENT_HOST_HOME=$HostRoot",
    "-e", "CODE_AGENT_HOST_ROOT=$HostRoot"
)
$found = @()
foreach ($name in $hostVars) {
    $val = [Environment]::GetEnvironmentVariable($name, "Process")
    if (-not $val) { $val = [Environment]::GetEnvironmentVariable($name, "User") }
    if (-not $val) { $val = [Environment]::GetEnvironmentVariable($name, "Machine") }
    if ($val) {
        Set-Item -Path "Env:$name" -Value $val
        $envArgs += @("-e", $name)
        $found += $name
    }
}

if ($found.Count -eq 0) {
    Write-Host "Warning: no API keys in host env (set GEMINI_API_KEY or OPENAI_API_KEY, etc.)"
} else {
    Write-Host "Passing host env: $($found -join ' ')"
}

if (-not $NoPull) {
    $null = docker image inspect $Image 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Pulling $Image ..."
        docker pull $Image
        if ($LASTEXITCODE -ne 0) {
            Write-Host ""
            Write-Host "Pull failed. If private: docker login ghcr.io -u YOUR_GITHUB_USER"
            exit 1
        }
    } else {
        Write-Host "Using local image: $Image"
    }
}

$envFileArgs = @()
$dotenv = Join-Path $Root ".env"
if (Test-Path $dotenv) {
    $envFileArgs = @("--env-file", $dotenv)
}

$volumeArgs = @("-v", "${HostRoot}:${HostRoot}")
if (-not ($Workspace.StartsWith($HostRoot, [System.StringComparison]::OrdinalIgnoreCase))) {
    $volumeArgs += @("-v", "${Workspace}:${Workspace}")
}

Write-Host ""
Write-Host "Chat UI → http://127.0.0.1:$Port"
Write-Host "Host root (browse): $HostRoot"
Write-Host "Workspace:          $Workspace"
Write-Host "Image:              $Image"
Write-Host ""

docker run --rm -it `
  @envFileArgs `
  @envArgs `
  -p "${Port}:8080" `
  @volumeArgs `
  -w $Workspace `
  $Image `
  web serve --host 0.0.0.0 --port 8080 -w $Workspace
