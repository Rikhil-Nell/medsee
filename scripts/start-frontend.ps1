#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location (Join-Path (Split-Path $PSScriptRoot -Parent) "frontend")
npm install
npm run dev
