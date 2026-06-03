<#
.SYNOPSIS
Deploys SharePoint libraries, content types, and metadata columns for Copilot Studio.
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
Write-Host "Creating site collection artifacts at $siteUrl"

# Create libraries
$libraries = @("AgentKnowledge", "GovernanceArtifacts", "AgentAssets", "ExternalFeeds")
foreach ($library in $libraries) {
    if (-not (Get-PnPList -Identity $library -ErrorAction SilentlyContinue)) {
        Write-Host "Creating library: $library"
        Add-PnPList -Title $library -Template DocumentLibrary -EnableVersioning $true -OnQuickLaunch $true
    } else {
        Write-Host "Library already exists: $library"
    }
}

# Create standard site columns
$columns = @(
    @{ InternalName = "BusinessUnit"; DisplayName = "BusinessUnit"; Type = "Choice"; Choices = @("Finance","HR","Legal","Sales","IT","Operations") },
    @{ InternalName = "KnowledgeDomain"; DisplayName = "KnowledgeDomain"; Type = "Text" },
    @{ InternalName = "ContentType"; DisplayName = "ContentType"; Type = "Choice"; Choices = @("Policy","Runbook","FAQ","Procedure","Contract") },
    @{ InternalName = "SourceSystem"; DisplayName = "SourceSystem"; Type = "Text" },
    @{ InternalName = "SensitivityLabel"; DisplayName = "SensitivityLabel"; Type = "Choice"; Choices = @("Public","Internal","Confidential","Highly Confidential") },
    @{ InternalName = "RetentionLabel"; DisplayName = "RetentionLabel"; Type = "Choice"; Choices = @("1 year","3 years","7 years","Permanent") },
    @{ InternalName = "RAGPriority"; DisplayName = "RAGPriority"; Type = "Choice"; Choices = @("High","Normal","Low") },
    @{ InternalName = "Language"; DisplayName = "Language"; Type = "Choice"; Choices = @("en-US","local") },
    @{ InternalName = "EffectiveDate"; DisplayName = "EffectiveDate"; Type = "DateTime" },
    @{ InternalName = "ApprovedBy"; DisplayName = "ApprovedBy"; Type = "User" }
)

foreach ($column in $columns) {
    if (-not (Get-PnPField -Identity $column.InternalName -ErrorAction SilentlyContinue)) {
        Write-Host "Creating field: $($column.DisplayName)"
        Add-PnPField -DisplayName $column.DisplayName -InternalName $column.InternalName -Type $column.Type -Group "Copilot Studio" -AddToDefaultView
        if ($column.Type -eq "Choice") {
            Set-PnPField -Identity $column.InternalName -Choices $column.Choices
        }
    } else {
        Write-Host "Field already exists: $($column.DisplayName)"
    }
}

# Content type creation
$contentTypes = @(
    @{ Name = "AgentKnowledgeItem"; Description = "Generic knowledge item used for RAG." },
    @{ Name = "PolicyDocument"; Description = "Formal policy or regulation document." },
    @{ Name = "AgentBlueprint"; Description = "Agent design and workflow blueprint." },
    @{ Name = "ComplianceArtifact"; Description = "Audit and compliance evidence." },
    @{ Name = "OperationalRunbook"; Description = "Operational runbook document." }
)

foreach ($contentType in $contentTypes) {
    if (-not (Get-PnPContentType -Identity $contentType.Name -ErrorAction SilentlyContinue)) {
        Write-Host "Creating content type: $($contentType.Name)"
        Add-PnPContentType -Name $contentType.Name -Description $contentType.Description -Group "Copilot Studio"
        Add-PnPContentTypeField -ContentType $contentType.Name -Field "BusinessUnit"
        Add-PnPContentTypeField -ContentType $contentType.Name -Field "KnowledgeDomain"
        Add-PnPContentTypeField -ContentType $contentType.Name -Field "ContentType"
        Add-PnPContentTypeField -ContentType $contentType.Name -Field "SourceSystem"
        Add-PnPContentTypeField -ContentType $contentType.Name -Field "SensitivityLabel"
        Add-PnPContentTypeField -ContentType $contentType.Name -Field "RetentionLabel"
        Add-PnPContentTypeField -ContentType $contentType.Name -Field "RAGPriority"
        Add-PnPContentTypeField -ContentType $contentType.Name -Field "Language"
        Add-PnPContentTypeField -ContentType $contentType.Name -Field "EffectiveDate"
        Add-PnPContentTypeField -ContentType $contentType.Name -Field "ApprovedBy"
    } else {
        Write-Host "Content type already exists: $($contentType.Name)"
    }
}

Write-Host "Deployment complete. Verify the site collection manually and apply metadata navigation views."
