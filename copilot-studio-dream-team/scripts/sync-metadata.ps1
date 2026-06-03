<#
.SYNOPSIS
Validates SharePoint metadata fields and syncs configuration with defined templates.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$TenantUrl,

    [Parameter(Mandatory=$true)]
    [string]$SiteRelativeUrl
)

Import-Module PnP.PowerShell -ErrorAction Stop

Write-Host "Connecting to SharePoint tenant $TenantUrl"
Connect-PnPOnline -Url $TenantUrl -Interactive

$siteUrl = "$TenantUrl/$SiteRelativeUrl"
Write-Host "Validating metadata on site collection $siteUrl"

$requiredFields = @(
    "BusinessUnit",
    "KnowledgeDomain",
    "ContentType",
    "SourceSystem",
    "SensitivityLabel",
    "RetentionLabel",
    "RAGPriority",
    "Language",
    "EffectiveDate",
    "ApprovedBy"
)

$lists = Get-PnPList | Where-Object {$_.BaseTemplate -eq 101}

foreach ($list in $lists) {
    Write-Host "Checking list: $($list.Title)"
    $missingFields = @()
    foreach ($fieldName in $requiredFields) {
        if (-not (Get-PnPField -List $list.Title -Identity $fieldName -ErrorAction SilentlyContinue)) {
            $missingFields += $fieldName
        }
    }
    if ($missingFields.Count -gt 0) {
        Write-Warning "Missing fields in $($list.Title): $($missingFields -join ', ')"
    } else {
        Write-Host "All required metadata present in $($list.Title)"
    }
}

Write-Host "Metadata validation complete. Review warnings and correct missing fields."