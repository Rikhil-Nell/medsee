#!/usr/bin/env pwsh
param(
    [Parameter(Mandatory = $true)]
    [string]$Image,

    [Parameter(Mandatory = $true)]
    [ValidateSet("MRI", "CT", "XRAY")]
    [string]$Modality,

    [Parameter(Mandatory = $true)]
    [string]$BodyPart,

    [string]$ClinicalContext = "POC endpoint test",
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path $PSScriptRoot -Parent
$imagePath = if ([System.IO.Path]::IsPathRooted($Image)) { $Image } else { Join-Path $root $Image }

if (-not (Test-Path $imagePath)) {
    throw "Image not found: $imagePath"
}

$metadata = @{
    modality = $Modality
    body_part = $BodyPart
    clinical_context = $ClinicalContext
} | ConvertTo-Json -Compress

curl.exe -X POST "$BaseUrl/reports" `
    -F "image=@$imagePath" `
    -F "metadata=$metadata"
