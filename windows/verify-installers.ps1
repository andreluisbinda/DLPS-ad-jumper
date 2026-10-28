$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
try {
    $Manifest = Get-Content -LiteralPath (Join-Path $Root 'installers-manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($Item in $Manifest.files) {
        if ([IO.Path]::GetFileName($Item.filename) -ne $Item.filename) { throw 'Nome invalido no manifesto.' }
        $File = Join-Path (Join-Path $Root 'installers') $Item.filename
        if (-not (Test-Path -LiteralPath $File)) { throw "Instalador opcional ausente: $($Item.filename). Veja installers/LEIA-ME.md para obter na fonte oficial." }
        $Digest = (Get-FileHash -LiteralPath $File -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($Digest -ne $Item.sha256) { throw "SHA256 divergente em $($Item.filename)" }
        $Signature = Get-AuthenticodeSignature -LiteralPath $File
        if ($Signature.Status -ne 'Valid') { throw "Assinatura nao validada: $($Item.filename) - $($Signature.Status). Nenhum instalador foi aberto." }
        Write-Host ("OK: " + $Item.filename + ' | Assinante: ' + $Signature.SignerCertificate.Subject)
    }
    Write-Host 'Verificacao concluida. Nenhum instalador foi executado.'
    exit 0
} catch { Write-Host ('ERRO: ' + $_.Exception.Message) -ForegroundColor Red; exit 1 }
