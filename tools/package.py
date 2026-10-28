"""Create a transferable offline ZIP using only an explicit project allowlist."""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_ROOT = {'README.md','LEIA-ME-PRIMEIRO.txt','resolver.py','requirements.txt','requirements-lock.txt','downloads-manifest.json','installers-manifest.json','PREPARAR.cmd','RESOLVER.cmd','VERIFICAR_INSTALADORES.cmd','.gitignore','.gitattributes'}
ALLOWED_DIRS = {'extension','windows','tests','docs','downloads','installers','tools'}

def validate():
    for manifest, folder in [('downloads-manifest.json','downloads'),('installers-manifest.json','installers')]:
        for f in json.loads((ROOT/manifest).read_text(encoding='utf-8'))['files']:
            p = ROOT/folder/f['filename']
            if not p.is_file() or p.stat().st_size != f['size'] or hashlib.sha256(p.read_bytes()).hexdigest() != f['sha256']:
                raise ValueError(f'Arquivo ausente ou hash divergente: {p}')

if __name__ == '__main__':
    validate()
    target = Path(sys.argv[1]) if len(sys.argv)>1 else ROOT.parent/'dlps-links-windows-offline.zip'
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(ROOT.rglob('*')):
            rel = p.relative_to(ROOT)
            if not p.is_file() or p.is_symlink() or '__pycache__' in rel.parts or p.resolve()==target.resolve(): continue
            if (len(rel.parts)==1 and p.name in ALLOWED_ROOT) or rel.parts[0] in ALLOWED_DIRS:
                z.write(p,Path('dlps-links-windows')/rel)
    print(f'ZIP criado: {target} ({target.stat().st_size/1024/1024:.1f} MiB)')
