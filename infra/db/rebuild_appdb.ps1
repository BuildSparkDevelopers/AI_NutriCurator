param(
    [switch]$WithData
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Run-Step {
    param(
        [string]$Title,
        [scriptblock]$Action
    )
    Write-Host ""
    Write-Host "== $Title ==" -ForegroundColor Cyan
    & $Action
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path

Push-Location $repoRoot
try {
    $schemaHostPath = "infra/db/appdb_schema_only.sql"
    $dataHostPath = "infra/db/appdb_data_dump.sql"
    $schemaContainerPath = "/tmp/appdb_schema_only.sql"
    $dataContainerPath = "/tmp/appdb_data_dump.sql"

    Run-Step "Start postgres container" {
        docker compose up -d postgres
    }

    Run-Step "Export current schema from appdb" {
        docker compose exec -T postgres pg_dump -U appuser -d appdb --schema-only --no-owner --no-privileges -f $schemaContainerPath
        docker cp "app-postgres:$schemaContainerPath" $schemaHostPath
    }

    Run-Step "Drop and recreate appdb" {
        docker compose exec -T postgres psql -U appuser -d postgres -c "DROP DATABASE IF EXISTS appdb;"
        docker compose exec -T postgres psql -U appuser -d postgres -c "CREATE DATABASE appdb;"
    }

    Run-Step "Apply schema to new appdb" {
        docker cp $schemaHostPath "app-postgres:$schemaContainerPath"
        docker compose exec -T postgres psql -U appuser -d appdb -f $schemaContainerPath
    }

    if ($WithData) {
        if (-not (Test-Path $dataHostPath)) {
            throw "Data dump not found: $dataHostPath"
        }

        Run-Step "Apply data dump to appdb" {
            docker cp $dataHostPath "app-postgres:$dataContainerPath"
            docker compose exec -T postgres psql -U appuser -d appdb -f $dataContainerPath
        }
    }

    Run-Step "Verify database objects" {
        docker compose exec -T postgres psql -U appuser -d appdb -c "\dt+ public.*"
    }

    Write-Host ""
    Write-Host "Done. appdb rebuild completed." -ForegroundColor Green
    if ($WithData) {
        Write-Host "Data restore included from $dataHostPath" -ForegroundColor Green
    }
}
finally {
    Pop-Location
}
