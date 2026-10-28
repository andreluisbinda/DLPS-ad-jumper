# DLPS Links — kit para Windows 10 x64

A extensão recupera os destinos públicos dos botões do DLPSGAME e abre os links originais, evitando o wrapper de anúncios conhecido. O resolvedor Python faz a mesma extração pelo terminal e exporta JSON. O destino ainda pode exigir Cloudflare ou CAPTCHA.

O kit contém os arquivos necessários para executar o projeto no outro PC. Os arquivos de jogos não fazem parte dele.

## Usar somente a extensão

Não precisa de Python nem de PREPARAR.cmd:

1. Extraia o ZIP para uma pasta permanente, por exemplo `C:\Ferramentas\dlps-links-windows`.
2. Caso o Chrome ainda não esteja instalado, veja `installers/LEIA-ME.md`.
3. No Chrome, abra `chrome://extensions`, ative **Modo do desenvolvedor** e clique em **Carregar sem compactação**.
4. Escolha a pasta `extension` dentro deste kit.
5. Abra a página do jogo no DLPSGAME e use **DLPS · Links diretos**, no canto inferior direito.

O Chrome exige esse carregamento manual para a extensão local; os scripts não alteram seu perfil nem instalam a extensão silenciosamente. Os detalhes de funcionamento e limites estão em [extension/README.md](extension/README.md).

## Usar o resolvedor pelo terminal

O ZIP completo inclui Python 3.14.10 portátil x64 e as bibliotecas. Não precisa instalar Python no sistema, alterar o PATH, instalar pip nem executar como administrador.

1. Abra `PREPARAR.cmd`. Ele verifica SHA-256 e extrai o runtime local em `.runtime`.
2. Abra `RESOLVER.cmd` e cole a URL solicitada. A entrada é passada como argumento, sem montar comandos a partir do conteúdo dos sites.
3. Leia o resultado na janela. O JSON fica na pasta `resultados`.

Também pode usar o terminal, dentro da pasta do kit:

```bat
PREPARAR.cmd -Offline
RESOLVER.cmd "https://dlpsgame.com/marvels-spider-man-ps4-pkg/" --json "resultados\spider.json"
```

Somente JSON:

```bat
RESOLVER.cmd "https://dlpsgame.com/marvels-spider-man-ps4-pkg/" --json -
```

O modo `-Offline` vale para preparar o ambiente com os arquivos transferidos; a investigação das páginas depende de internet. Sem `-Offline`, o preparador baixa os arquivos obrigatórios que faltarem a partir das URLs oficiais fixadas no manifesto. Arquivos com hash divergente são recusados.

Mais opções da CLI: `--timeout 20`, `--interval 1`, `--max-redirects 8`, `--cache PASTA`, `--refresh`. O cache padrão dura 24 horas, inclusive para HTTP 403. O código de saída 0 indica extração de opções da origem; confira `destinations[*].resolution_status` no JSON para saber se o destino foi resolvido. Código 2 indica falha na origem ou nenhuma opção reconhecida.

Os `.cmd` executam scripts PowerShell locais com `-NoProfile` e permissão de execução restrita ao processo lançado. Não alteram a política permanente do PowerShell. Todos os arquivos do ambiente Python permanecem nesta pasta. Para remover o runtime, apague `.runtime`; para remover o projeto, remova a extensão no Chrome e apague a pasta.

## Chrome e Git, se o Windows estiver sem eles

A pasta `installers` do ZIP inclui os instaladores oficiais x64 do Chrome e do Git. São opcionais e não são executados pelo preparador. `VERIFICAR_INSTALADORES.cmd` confere SHA-256 e pede ao Windows a validação das assinaturas Authenticode; não instala programas. Depois da conferência, abra manualmente o instalador desejado. Instalações do Chrome/Git podem solicitar permissões do Windows e são independentes do runtime portátil do projeto.

Para transferir o ZIP, Git não é necessário. Para o futuro `git clone`, instale o Git primeiro se estiver ausente. URLs oficiais e proveniência estão em [installers/LEIA-ME.md](installers/LEIA-ME.md) e `installers-manifest.json`.

## Depois que publicarmos no GitHub

Ainda não há repositório remoto criado ou publicado. Depois da publicação, o fluxo será:

```bat
git clone URL_DO_REPOSITORIO
cd PASTA_DO_REPOSITORIO
PREPARAR.cmd
```

A cópia via Git conterá código, documentação, hashes e versões; os binários pesados não entram no histórico. `PREPARAR.cmd` baixa o runtime e as bibliotecas com conferência de SHA-256. Para usar só a extensão, nem esse passo será necessário: carregue a pasta `extension`.

O ZIP completo é a entrega para transferência direta e poderá ser anexado a uma Release do GitHub depois. Para gerar novamente o ZIP em uma máquina com todos os arquivos presentes:

```bat
.runtime\python\python.exe -X utf8 tools\package.py
```

O empacotador verifica os hashes e inclui apenas uma lista explícita de pastas do projeto, excluindo `.git`, ambientes, caches e resultados. Os instaladores do Chrome e Git também precisam estar presentes para gerar o kit offline completo.

## O que está incluído

| Caminho | Conteúdo |
| --- | --- |
| `extension/` | Extensão Chrome Manifest V3, sem dependências Python |
| `resolver.py` | Resolvedor CLI |
| `PREPARAR.cmd` / `RESOLVER.cmd` | Preparação e execução no Windows |
| `windows/` | Scripts PowerShell locais |
| `downloads/` | Python portátil e oito wheels, no ZIP completo |
| `installers/` | Chrome e Git oficiais x64, opcionais no ZIP completo |
| `downloads-manifest.json` | URLs, versões, tamanhos e hashes obrigatórios |
| `installers-manifest.json` | Proveniência e hashes dos instaladores opcionais |
| `requirements-lock.txt` | Dependências Python e hashes fixados |
| `tests/` | Testes sem rede e trechos públicos usados como fixtures |
| `docs/` | Descobertas, validação e resultados dos testes anteriores |

A distribuição Python embeddable e suas dependências são usadas como componentes locais deste aplicativo, sem pip nem um ambiente global. As licenças originais acompanham os arquivos dos fornecedores. [Python oficial](https://www.python.org/downloads/release/python-31410/) e [documentação do pacote embeddable](https://docs.python.org/3.14/using/windows.html#the-embeddable-package).

## Validação e limites

O resolvedor foi testado no Debian com as páginas reais de Spider-Man e God of War Ragnarok. A extensão foi carregada no Chromium e testada com os trechos reais e o script de reescrita capturado; o clique abriu diretamente a URL esperada sem solicitar clk.sh/full. Os arquivos empacotados e seus hashes foram conferidos. A preparação nativa do Windows e as assinaturas Authenticode precisam ser confirmadas no PC Windows: não foi executado um Windows neste Debian.

Testes locais após a preparação:

```bat
.runtime\python\python.exe -X utf8 -m unittest discover -s tests -v
```

A ferramenta não baixa jogos, não percorre números de `/archives/`, não envia formulários nem resolve CAPTCHA. Um vínculo confirmado na origem não comprova o conteúdo ou a disponibilidade do destino. A extensão não verifica arquivos por malware. O relatório detalha exatamente o bloqueio encontrado: [docs/INVESTIGACAO.md](docs/INVESTIGACAO.md).
