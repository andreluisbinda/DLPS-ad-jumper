param([Parameter(ValueFromRemainingArguments = $true)][string[]]$ResolverArgs)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Exe = Join-Path $Root '.runtime\python\python.exe'
if (-not (Test-Path -LiteralPath $Exe)) {
    Write-Host 'Primeiro execute PREPARAR.cmd. Nao e necessario instalar Python no sistema.'
    exit 1
}
if (-not $ResolverArgs -or $ResolverArgs.Count -eq 0) {
    $GameUrl = Read-Host 'Cole a URL da pagina do jogo'
    if ([string]::IsNullOrWhiteSpace($GameUrl)) { exit 1 }
    $OutputDir = Join-Path $Root 'resultados'
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    $JsonFile = Join-Path $OutputDir ((Get-Date -Format 'yyyyMMdd-HHmmss-fff') + '.json')
    $ResolverArgs = @($GameUrl, '--json', $JsonFile)
    Write-Host "JSON sera salvo em $JsonFile"
}
& $Exe -X utf8 (Join-Path $Root 'resolver.py') @ResolverArgs
exit $LASTEXITCODE
