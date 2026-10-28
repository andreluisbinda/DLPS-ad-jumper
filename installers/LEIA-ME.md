# Instaladores opcionais para Windows x64

O kit completo inclui os instaladores oficiais do Google Chrome e Git for Windows, apenas para o caso de o outro PC ainda não tê-los. Nenhum instalador foi executado no Debian, nem é aberto automaticamente por PREPARAR.cmd.

- Google Chrome: `googlechromestandaloneenterprise64.msi`, pacote offline do próprio Google. Execute manualmente para instalar; o Windows pode solicitar administrador. Não aplica políticas de organização por conta deste projeto.
- Git for Windows: `Git-2.56.0.4-64-bit.exe`, obtido da release oficial indicada por git-scm.com. Execute manualmente e depois abra um terminal novo para usar `git clone`.

Antes de instalar, `VERIFICAR_INSTALADORES.cmd` compara os hashes e pede ao Windows a validação Authenticode. Ele só verifica; não executa os instaladores. A validação de certificados pode depender da conectividade e das autoridades certificadoras presentes no Windows recém-instalado. Os hashes foram conferidos no Debian, mas a validação Authenticode nativa ainda precisa ocorrer no Windows.

Os binários não entram no Git. Depois de clonar, use as páginas oficiais abaixo se precisar deles; Git já estará disponível caso você tenha feito o clone pelo terminal. O hash de um instalador novo pode diferir do pacote capturado neste kit. A URL genérica do Google oferece versões atualizadas, portanto não se espera que o hash antigo coincida com todo download futuro.

- Chrome: https://www.google.com/chrome/
- Chrome offline: https://chromeenterprise.google/download/
- Git: https://git-scm.com/install/windows

Proveniência, tamanho e SHA-256 dos arquivos incluídos: `../installers-manifest.json` e `SHA256SUMS.txt`.
