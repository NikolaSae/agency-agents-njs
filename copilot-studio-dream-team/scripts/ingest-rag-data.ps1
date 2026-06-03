<#
.SYNOPSIS
Preparation script for ingesting SharePoint documents into a hybrid RAG vector store.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$TenantUrl,

    [Parameter(Mandatory=$true)]
    [string]$SiteRelativeUrl,

    [Parameter(Mandatory=$true)]
    [string]$VectorStoreEndpoint,

    [Parameter(Mandatory=$true)]
    [string]$ApiKey
)

Import-Module PnP.PowerShell -ErrorAction Stop

Write-Host "Connecting to SharePoint tenant $TenantUrl"
Connect-PnPOnline -Url $TenantUrl -Interactive

$siteUrl = "$TenantUrl/$SiteRelativeUrl"
Write-Host "Preparing RAG ingestion from $siteUrl"

# Retrieve AgentKnowledge documents
$docs = Get-PnPListItem -List "AgentKnowledge" -Fields "Title","FileRef","BusinessUnit","KnowledgeDomain","ContentType","SensitivityLabel","RetentionLabel","RAGPriority","Language","EffectiveDate","ApprovedBy"

foreach ($doc in $docs) {
    $metadata = [ordered]@{
        Title = $doc["Title"]
        SourceURI = $doc["FileRef"]
        BusinessUnit = $doc["BusinessUnit"]
        KnowledgeDomain = $doc["KnowledgeDomain"]
        ContentType = $doc["ContentType"]
        SensitivityLabel = $doc["SensitivityLabel"]
        RetentionLabel = $doc["RetentionLabel"]
        RAGPriority = $doc["RAGPriority"]
        Language = $doc["Language"]
        EffectiveDate = $doc["EffectiveDate"]
        ApprovedBy = $doc["ApprovedBy"]
    }

    if ($metadata.SensitivityLabel -eq "Highly Confidential") {
        Write-Host "Skipping highly confidential document: $($metadata.Title)"
        continue
    }

    Write-Host "Preparing ingestion for: $($metadata.Title)"

    # Download file content temporarily
    $file = Get-PnPFile -Url $metadata.SourceURI -AsFile -Path $env:TEMP -FileName ([IO.Path]::GetFileName($metadata.SourceURI)) -Force
    $content = Get-Content -Path $file.FullName -Raw

    # Prepare payload to ingestion endpoint
    $payload = @{ 
        sourceUri = $metadata.SourceURI
        content = $content
        metadata = $metadata
    } | ConvertTo-Json -Depth 5

    Write-Host "Uploading document to vector store: $($metadata.Title)"
    $response = Invoke-RestMethod -Uri $VectorStoreEndpoint -Method Post -Headers @{"Authorization" = "Bearer $ApiKey"; "Content-Type" = "application/json"} -Body $payload
    Write-Host "Ingestion response status: $($response.status)"
}

Write-Host "RAG ingestion script completed. Verify vector store index and metadata payloads."