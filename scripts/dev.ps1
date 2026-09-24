#!/usr/bin/env pwsh
# Convenience alias — use start-backend.ps1 for options (port, no-reload).
& (Join-Path $PSScriptRoot "start-backend.ps1") @args
