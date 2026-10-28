# Investigação de 28/10/2026

Origem: https://dlpsgame.com/marvels-spider-man-ps4-pkg/

O HTML original contém `.secure-data[data-payload]` dentro de cada botão `.su-spoiler`. O payload é HTML em Base64 UTF-8; a implementação da própria página usa `atob` para decodificá-lo. Os trechos pertinentes estão em `tests/fixtures/spider.html` e o decoder público capturado em `tests/fixtures/source-decoder.js`.

O script https://clk.sh/js/full-page-script.js reescreve os links para `clk.sh/full?...&url=BASE64_DO_HREF&type=2`. O código capturado está em `tests/fixtures/clk-script.js`. O Chromium confirmou que o primeiro link “Viki” vira um wrapper cujo parâmetro decodifica exatamente para `https://downloadgameps3.net/archives/19078`.

Relações explicitamente publicadas no botão Link Download:

| Edição | Componente | Página |
| --- | --- | --- |
| CUSA11993 EUR v1.19 | Jogo base | https://downloadgameps3.net/archives/19078 |
| CUSA11993 EUR v1.19 | Update 1.19 (6.72+) | https://downloadgameps3.net/archives/19088 |
| CUSA11993 EUR v1.19 | Update 1.19 (Fix 5.05) | https://downloadgameps3.net/archives/19084 |
| CUSA11993 EUR v1.19 | DLC | https://downloadgameps3.net/archives/19094 |
| CUSA11993 EUR v1.19 | Mirror dos DLC | https://downloadgameps3.net/archives/6981 |
| CUSA02299 USA v1.19 @Fugazi | Update 1.19 (6.72+)(60fps) | https://downloadgameps3.net/archives/18816 |

Todos esses destinos retornaram HTTP 403 com o desafio “Just a moment...” do Cloudflare. O navegador também permaneceu na verificação. Assim, a associação está confirmada no href publicado pela origem, mas o conteúdo dos destinos e a ordem real das partes não puderam ser corroborados.

O wrapper real do primeiro botão respondeu HTTP 301 para `https://clksz.com/70YFXp`; a resposta seguinte, HTTP 200, pediu CAPTCHA. Nenhum formulário foi enviado. O destino já podia ser recuperado dos dados públicos antes dessa etapa.

As sete opções do Spider-Man incluem CUSA11993 Download e Mirror, CUSA11994 EUR v1.19, CUSA11995 EUR v1.17 e três variantes CUSA02299 USA. Algumas apontam diretamente a hospedagens/containers e não precisam de uma página intermediária `/archives/`.

A busca dirigida por CUSA11993, API WordPress, robots e sitemap de downloadgameps3.net também foram bloqueados por 403. A API da origem `/wp-json/wp/v2/posts/80409` retornou 403; o sitemap e a busca da origem estavam acessíveis. O post ID 80409 não foi usado para deduzir IDs do outro domínio.

Os exemplos `/archives/38700` e `/archives/38600` informados pelo usuário foram consultados individualmente, retornaram 403 e continuam sem identificação. Não foram associados ao Spider-Man. Não houve enumeração de IDs.

Teste adicional: https://dlpsgame.com/god-of-war-ragnarok-ps4-pkg/ — seis opções e cinco destinos explicitamente referenciados, também bloqueados no destino. O trecho público de teste está em `tests/fixtures/ragnarok.html`.

`Guide Download` em `/archives/18667` é um guia; não é tratado como componente do jogo. Rótulos sem href não viram links inventados. Containers e pastas de hospedagem são preservados; a CLI não os acessa.

Falta uma resposta legível do destino, após a verificação normal do site, para completar a cadeia até os links e partes internos. A extensão usa a sessão normal do navegador ao abrir o destino, mas não tenta solucionar desafios por conta própria.
