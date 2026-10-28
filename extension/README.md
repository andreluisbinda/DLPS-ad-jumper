# Extensão DLPS — Links diretos

Não precisa de Python, servidor, conta ou chave. A extensão usa Manifest V3 e scripts locais; atua apenas em dlpsgame.com, downloadgameps3.net e clk.sh/full.

No Chrome:

1. Abra `chrome://extensions`.
2. Ative **Modo do desenvolvedor**.
3. Clique em **Carregar sem compactação**.
4. Selecione esta pasta `extension`, que contém `manifest.json`.
5. Recarregue a página de um jogo do DLPSGAME.

No canto inferior direito, abra **DLPS · Links diretos**, escolha a edição e clique no componente desejado. O painel usa os hrefs originais publicados, recuperados do payload Base64 ou do wrapper conhecido de clk.sh. Também corrige hrefs que o script da página reescreva para esse wrapper. O texto de cada link mostra seu destino e a evidência ao passar o mouse.

O painel preserva CUSA, região e versão no cabeçalho, e jogo base, atualização e DLC em linhas separadas. Um rótulo sem href não gera um destino inventado. O clique abre o destino em nova aba; a extensão não baixa jogos por conta própria e não verifica a segurança ou a disponibilidade dos arquivos.

Essa versão evita os anúncios do encurtador quando o destino está publicamente disponível nos formatos observados. Não é um bloqueador geral de anúncios da página e não resolve tokens opacos, CAPTCHA, login ou o desafio do Cloudflare. `/archives/38700` e `/archives/38600` não foram associados ao Spider-Man.

Se uma URL `clk.sh/full` chegar a servir HTML, a extensão também pode encaminhá-la a uma página `/archives/` expressamente codificada no parâmetro. Porém, uma resposta HTTP 301 pode ocorrer antes de qualquer script da extensão executar; o caminho confiável é abrir o jogo e usar o painel de links diretos na origem. Ela não tenta resolver `/70YFXp` ou outros códigos opacos sem evidência.

Para atualizar após `git pull`, clique em **Recarregar** no cartão da extensão e recarregue a página. Mantenha esta pasta no mesmo caminho. Para remover, use **Remover** no Chrome.

Testada carregada no Chromium com os trechos reais salvos de Spider-Man e God of War Ragnarok e o script real capturado de clk.sh. Os testes interceptaram o tráfego com fixtures locais; o clique do painel chegou diretamente à URL esperada sem pedir clk.sh/full. O conteúdo real do destino continua sujeito ao bloqueio observado na investigação. Veja `../docs/extension-tests.json`.
