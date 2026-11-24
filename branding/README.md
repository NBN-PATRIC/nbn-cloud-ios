# NBN Cloud: app iOS

Fork do [ownCloud iOS](https://github.com/owncloud/ios-app) 12.7.1 com a marca da NBN Telecom, distribuído sob a mesma
licença (GNU GPL versão 3, arquivo `LICENSE`). ownCloud é marca registrada da ownCloud GmbH; este projeto não é
afiliado à ownCloud GmbH nem endossado por ela.

Código-fonte de cada versão: este repositório, ramo `nbn/12.7` (o `ios-sdk` é submódulo e aponta para o
`owncloud/ios-sdk` na mesma versão do upstream).

## Servidores

O mesmo app fala com o servidor ownCloud clássico (10.x e 11.x) e com o ownCloud Infinite Scale, com várias contas
ao mesmo tempo, em servidores diferentes. O SDK da versão 12.7.1 traz os três métodos de login e escolhe sozinho, na
ordem: OpenID Connect (Infinite Scale), OAuth2 (servidor clássico com o app oauth2) e senha (servidor clássico sem
oauth2). O login OAuth2 e o OIDC usam o cliente do ownCloud iOS, com retorno `oc://ios.owncloud.com`, que os
servidores já trazem cadastrado; por isso esse retorno não muda.

## O que muda em relação ao ownCloud iOS

- Marca pelo mecanismo oficial do app: `ownCloud/Resources/Theming/Branding.plist` (nome, cores, servidor sugerido,
  links) e as imagens em `ownCloud/Resources/Theming/branding-assets/` e no `AppIcon`. As imagens saem de
  `branding/tools/gerar_marca_ios.py` (Pillow), a partir de `branding/tools/logo-nbn.jpg`, com o mesmo desenho do
  NBN Cloud Android e desktop.
- Servidor sugerido ao adicionar conta (`branding.profile-url`), sem travar: o campo vem preenchido e pode ser trocado.
- Sem pedido de avaliação e sem os links de ajuda, privacidade e envio de comentários do ownCloud. Em
  Configurações, "Documentação" abre esta página e "Termos de uso" abre a licença.
- Identidade própria, para conviver com o app do ownCloud no mesmo iPhone: bundle id `br.com.nbntelecom.cloud`
  (extensões com os mesmos sufixos do upstream), app group e grupo do chaveiro `group.br.com.nbntelecom.cloud`,
  nome exibido "NBN Cloud" no app, no Arquivos e nas extensões, e link do app `nbncloud://`. Aplicada por
  `branding/ios/aplicar-identidade.sh`, que serve também para refazer a troca depois de trazer uma versão nova do
  upstream.

## Compilar

O GitHub Actions (`.github/workflows/nbn-ios.yml`) compila o app para o simulador, sem assinatura, e confere o bundle
id, o nome e as imagens da marca. No Mac, com o Xcode pedido em `.xcode-version`:

```
git submodule update --init
xcodebuild -project ownCloud.xcodeproj -scheme ownCloud -sdk iphonesimulator \
  -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO build
```

## Instalar em iPhone: o que falta

Todo app de iPhone precisa ser assinado por uma conta do Apple Developer Program. Sem ela, o app só roda no
simulador. Para instalar:

1. Conta Apple Developer da NBN (organização, com número D-U-N-S, ou individual). Ela dá o Team ID.
2. No portal da Apple: registrar os 6 bundle ids (`br.com.nbntelecom.cloud` e as 5 extensões), o app group
   `group.br.com.nbntelecom.cloud`, o certificado de distribuição e um perfil de provisionamento por alvo.
3. Assinar no Mac pela lane do fastlane, com tudo vindo do ambiente (nada disso entra no repositório):

   ```
   NBN_APPLE_TEAM_ID=<team id> NBN_SIGN_IDENTITY="Apple Distribution: <nome> (<team id>)" \
   NBN_EXPORT_METHOD=ad-hoc bundle exec fastlane nbn_build
   ```

4. Distribuir: ad hoc (aparelhos cadastrados pelo identificador, até 100 por ano), TestFlight (teste por até 90
   dias por build), App Store, ou app personalizado pelo Apple Business Manager (só para as empresas escolhidas).

O projeto ainda traz o time da ownCloud em `DEVELOPMENT_TEAM`; a lane troca pelo da NBN na hora de assinar.

Atenção à licença: a GPL versão 3 e os termos de uso da App Store têm conflito conhecido (a loja impõe restrições
que a GPL proíbe acrescentar). A ownCloud publica o app dela na loja como dona do código; um fork não tem essa
posição. O ad hoc não passa pela loja; App Store, app personalizado e TestFlight passam. Antes de publicar por esses
canais, a NBN precisa decidir isso com o jurídico (ou pedir autorização à ownCloud).

## Licença

GNU General Public License versão 3 (`LICENSE`), a mesma do ownCloud iOS.
