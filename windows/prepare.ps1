param([switch]$Offline, [switch]$VerifyOnly)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
$Root = Split-Path -Parent $PSScriptRoot
$Stage = $null
try {
    $NativeArch = $env:PROCESSOR_ARCHITECTURE
    if ($env:PROCESSOR_ARCHITEW6432) { $NativeArch = $env:PROCESSOR_ARCHITEW6432 }
    if ($NativeArch -ne 'AMD64') { throw 'Este kit e para Windows x64 (AMD64), nao ARM64 ou 32 bits.' }
    $Manifest = Get-Content -LiteralPath (Join-Path $Root 'downloads-manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $Downloads = Join-Path $Root 'downloads'
    New-Item -ItemType Directory -Force -Path $Downloads | Out-Null
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    foreach ($Item in $Manifest.files) {
        if ([IO.Path]::GetFileName($Item.filename) -ne $Item.filename) { throw 'Nome invalido no manifesto.' }
        $Uri = [Uri]$Item.url
        if ($Uri.Scheme -ne 'https' -or $Uri.Host -notin @('www.python.org', 'files.pythonhosted.org')) { throw 'Fonte nao autorizada no manifesto.' }
        $File = Join-Path $Downloads $Item.filename
        if (-not (Test-Path -LiteralPath $File)) {
            if ($Offline -or $VerifyOnly) { throw "Falta $($Item.filename). Copie o kit completo ou execute PREPARAR.cmd com internet." }
            Write-Host "Baixando $($Item.filename) da fonte oficial..."
            $Temporary = $File + '.part'
            try {
                Invoke-WebRequest -UseBasicParsing -Uri $Item.url -OutFile $Temporary -TimeoutSec 180 -MaximumRedirection 3
                $Digest = (Get-FileHash -LiteralPath $Temporary -Algorithm SHA256).Hash.ToLowerInvariant()
                if ($Digest -ne $Item.sha256) { throw "SHA256 divergente: $($Item.filename)" }
                Move-Item -LiteralPath $Temporary -Destination $File -Force
            } finally {
                if (Test-Path -LiteralPath $Temporary) { Remove-Item -LiteralPath $Temporary -Force }
            }
        }
        $Digest = (Get-FileHash -LiteralPath $File -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($Digest -ne $Item.sha256 -or (Get-Item -LiteralPath $File).Length -ne $Item.size) {
            throw "Arquivo divergente: $($Item.filename). Nao sera executado ou extraido."
        }
        Write-Host "OK SHA256: $($Item.filename)"
    }
    if ($VerifyOnly) { Write-Host 'Todos os arquivos obrigatorios conferem.'; exit 0 }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    function Expand-CheckedZip([string]$Zip, [string]$Destination) {
        New-Item -ItemType Directory -Force -Path $Destination | Out-Null
        $Base = [IO.Path]::GetFullPath($Destination).TrimEnd('\') + '\'
        $Archive = [IO.Compression.ZipFile]::OpenRead($Zip)
        try {
            foreach ($Entry in $Archive.Entries) {
                $Full = [IO.Path]::GetFullPath([IO.Path]::Combine($Destination, $Entry.FullName))
                if (-not $Full.StartsWith($Base, [StringComparison]::OrdinalIgnoreCase)) { throw 'Caminho inseguro no arquivo ZIP.' }
            }
        } finally { $Archive.Dispose() }
        [IO.Compression.ZipFile]::ExtractToDirectory($Zip, $Destination)
    }
    $Stage = Join-Path $Root ('.runtime-build-' + [Guid]::NewGuid().ToString('N'))
    $PythonDir = Join-Path $Stage 'python'
    $Vendor = Join-Path $Stage 'vendor'
    $PythonArchive = @($Manifest.files | Where-Object { $_.kind -eq 'python' })
    if ($PythonArchive.Count -ne 1) { throw 'O manifesto deve conter exatamente um Python.' }
    Expand-CheckedZip (Join-Path $Downloads $PythonArchive[0].filename) $PythonDir
    foreach ($Item in $Manifest.files | Where-Object { $_.kind -eq 'wheel' }) {
        if (-not $Item.filename.EndsWith('-none-any.whl')) { throw 'Este kit exige wheels Python puros e portaveis.' }
        Expand-CheckedZip (Join-Path $Downloads $Item.filename) $Vendor
    }
    # Isolated Python path: standard library, bundled packages and this project only.
    $Pth = "python314.zip`r`n.`r`n..\vendor`r`n..\..`r`n"
    [IO.File]::WriteAllText((Join-Path $PythonDir $Manifest.python_pth), $Pth, [Text.Encoding]::ASCII)
    $Exe = Join-Path $PythonDir 'python.exe'
    & $Exe -X utf8 -c "import ssl,requests,bs4; from resolver import parse_options; print('Python local e bibliotecas: OK')"
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao iniciar o Python local. A preparacao nao foi concluida.' }
    $Runtime = Join-Path $Root '.runtime'
    if (Test-Path -LiteralPath $Runtime) { Remove-Item -LiteralPath $Runtime -Recurse -Force }
    Move-Item -LiteralPath $Stage -Destination $Runtime
    $Stage = $null
    New-Item -ItemType Directory -Force -Path (Join-Path $Root 'resultados') | Out-Null
    Write-Host 'Pronto. Abra RESOLVER.cmd ou carregue a pasta extension no Chrome.'
    exit 0
} catch {
    Write-Host ('ERRO: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
} finally {
    if ($Stage -and (Test-Path -LiteralPath $Stage)) { Remove-Item -LiteralPath $Stage -Recurse -Force }
}
