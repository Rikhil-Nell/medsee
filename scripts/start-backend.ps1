#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start the Medsee FastAPI backend with hot reload.

.EXAMPLE
    .\scripts\start-backend.ps1

.EXAMPLE
    .\scripts\start-backend.ps1 -Port 8080 -NoReload
#>
param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$NoReload
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "Syncing dependencies..." -ForegroundColor Cyan
uv sync

$reloadFlag = if ($NoReload) { @() } else { @("--reload") }

Write-Host "Starting Medsee API at http://${HostName}:${Port}" -ForegroundColor Green
uv run uvicorn medsee.main:app @reloadFlag --host $HostName --port $Port
