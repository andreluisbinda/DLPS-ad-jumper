# Arquivos para o Python portátil

O ZIP de transferência inclui o pacote embeddable oficial do CPython 3.14.10 x64 e oito wheels puros. Não é necessário instalar Python no Windows, usar pip ou alterar o PATH.

As versões, URLs de origem, tamanhos e SHA-256 estão em `../downloads-manifest.json`. O hash do Python foi comparado ao publicado em python.org; os dos wheels, aos publicados pelo PyPI para cada versão. `PREPARAR.cmd` confere os hashes antes de extrair qualquer arquivo.

Os binários desta pasta não entram no Git. Depois de um `git clone`, `PREPARAR.cmd` baixa exatamente as versões fixadas e confere os hashes. No kit completo, `PREPARAR.cmd -Offline` usa apenas os arquivos já presentes. O modo offline se refere à preparação: consultar páginas de jogos continua precisando de internet.

Fontes oficiais:

- https://www.python.org/downloads/release/python-31410/
- https://docs.python.org/3.14/using/windows.html#the-embeddable-package
- https://pypi.org/

Os avisos de licença originais permanecem dentro do ZIP do Python e dos diretórios `.dist-info` dos wheels; são extraídos com os componentes.
