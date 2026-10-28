# Validação do kit

Preparado no Debian em 28/10/2026 para Windows 10 x64.

Verificações executadas:

- SHA-256 e tamanho dos nove downloads obrigatórios (Python portátil e oito wheels).
- SHA-256 e tamanho dos dois instaladores opcionais.
- Hash do Python comparado ao publicado na página oficial de lançamento; hashes dos wheels comparados aos metadados de cada versão no PyPI.
- Hash do Git comparado ao digest da release oficial no GitHub. O Chrome veio diretamente de dl.google.com; seu hash local foi registrado, sem alegar validação Authenticode no Debian.
- Integridade ZIP e presença do executável, DLL, biblioteca padrão e módulo SSL no pacote Python Windows.
- Sete testes do kit usando apenas as bibliotecas extraídas dos wheels transferidos, sem depender de pacotes instalados globalmente. Resultado em `tests-kit.txt`.
- Sintaxe JavaScript da extensão validada com `node --check`.
- Extensão realmente carregada no Chromium: sete verificações com fixtures de HTML e script reais capturados, incluindo clique direto e recusa de URL javascript:. Resultado em `extension-tests.json`.
- O código da extensão entregue é o mesmo testado. A documentação foi acrescentada depois.
- O repositório local tem `.gitignore` para excluir runtimes, caches, resultados e instaladores. Não foi criado repositório remoto nem feito push.

Limite: os comandos Windows, o runtime Windows e as assinaturas Authenticode dos instaladores não foram executados/validados nativamente, pois este ambiente é Debian e não dispõe de Windows/Wine. Os testes do resolvedor e das dependências foram executados no Python Linux. `PREPARAR.cmd` inclui uma verificação real de importação no runtime Windows antes de concluir; `VERIFICAR_INSTALADORES.cmd` pede a validação nativa das assinaturas no outro PC.

Os dez testes originais da investigação estão registrados separadamente em `tests.txt`; os sete testes atuais do kit não consultam sites.
