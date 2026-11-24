#!/bin/sh
# NBN Cloud iOS: aplica a identidade própria no projeto, para o app conviver com o ownCloud no mesmo iPhone.
#
#   sh branding/ios/aplicar-identidade.sh          (na raiz do repositório; repetir não estraga nada)
#
# O que muda (nada disso depende do time da Apple; o prefixo do time entra na hora de assinar, porque as
# entitlements usam $(AppIdentifierPrefix)):
#   - bundle id do app e das extensões: com.owncloud.ios-app[.sufixo] -> br.com.nbntelecom.cloud[.sufixo]
#   - app group e grupo do chaveiro: group.com.owncloud.ios-app -> group.br.com.nbntelecom.cloud
#     (o app principal já usa group.$(PRODUCT_BUNDLE_IDENTIFIER), que acompanha o bundle id)
#   - nome exibido: APP_PRODUCT_NAME = "NBN Cloud" (app, Arquivos, "Salvar no", "Compartilhar no")
#   - esquema de link do app: owncloud:// -> nbncloud://
# O que NÃO muda: o retorno do login OAuth2/OIDC (oc://ios.owncloud.com), que o servidor clássico e o
# Infinite Scale já trazem cadastrado para o app do ownCloud.
#
# Usado depois de trazer uma versão nova do upstream: volte estes arquivos ao do upstream e rode de novo.
set -eu

ANTIGO_ID='com.owncloud.ios-app'
NOVO_ID='br.com.nbntelecom.cloud'
ANTIGO_GRUPO='group.com.owncloud.ios-app'
NOVO_GRUPO='group.br.com.nbntelecom.cloud'
NOME='NBN Cloud'
ESQUEMA='nbncloud'
PYTHON=${PYTHON:-python3}

[ -f ownCloud.xcodeproj/project.pbxproj ] || { echo "rode na raiz do repositório" >&2; exit 1; }

troca() { # troca <arquivo> <expressão sed>
	sed -e "$2" "$1" > "$1.nbn" && mv "$1.nbn" "$1"
}

# 1. bundle ids (só nas linhas PRODUCT_BUNDLE_IDENTIFIER) e nome exibido
troca ownCloud.xcodeproj/project.pbxproj "/PRODUCT_BUNDLE_IDENTIFIER/s/\"$ANTIGO_ID/\"$NOVO_ID/"
troca ownCloud.xcodeproj/project.pbxproj "s/APP_PRODUCT_NAME = ownCloud;/APP_PRODUCT_NAME = \"$NOME\";/"

# 2. app group e grupo do chaveiro das extensões
for f in "ownCloud File Provider/Info.plist" "ownCloud File Provider/ownCloud_File_Provider.entitlements" \
	"ownCloud File Provider UI/Info.plist" "ownCloud File Provider UI/ownCloud_File_Provider_UI.entitlements" \
	"ownCloud Intents/Info.plist" "ownCloud Intents/ownCloud Intents.entitlements" \
	"ownCloud Share Extension/Info.plist" "ownCloud Share Extension/en.lproj/Info.plist" \
	"ownCloud Share Extension/ownCloud Share Extension.entitlements" \
	"ownCloud Action Extension/Info.plist" "ownCloud Action Extension/ownCloud Action Extension.entitlements"; do
	troca "$f" "s/$ANTIGO_GRUPO</$NOVO_GRUPO</g"
done

# 3. app principal: nome exibido e esquema de link
troca ownCloud/Resources/Info.plist '/<key>CFBundleDisplayName<\/key>/{n;s/\$(PRODUCT_NAME)/$(APP_PRODUCT_NAME)/;}'
troca ownCloud/Resources/Info.plist "s#<string octype=\"app\">owncloud</string>#<string octype=\"app\">$ESQUEMA</string>#"

# 4. "Salvar no ownCloud" / "Compartilhar no ownCloud" traduzidos (troca só o texto, sem reformatar o JSON)
$PYTHON - "$NOME" "ownCloud Action Extension/InfoPlist.xcstrings" "ownCloud Share Extension/InfoPlist.xcstrings" <<'PY'
import json, sys
nome = sys.argv[1]
for caminho in sys.argv[2:]:
    with open(caminho, encoding='utf-8') as f:
        texto = f.read()
    dados = json.loads(texto)
    locs = dados['strings'].get('CFBundleDisplayName', {}).get('localizations', {})
    for loc in locs.values():
        valor = loc.get('stringUnit', {}).get('value', '')
        if 'ownCloud' in valor:
            antigo = json.dumps(valor, ensure_ascii=False)
            novo = json.dumps(valor.replace('ownCloud', nome), ensure_ascii=False)
            texto = texto.replace('"value" : ' + antigo, '"value" : ' + novo)
    json.loads(texto)  # confere que continua JSON válido
    with open(caminho, 'w', encoding='utf-8', newline='') as f:
        f.write(texto)
PY

echo "identidade NBN aplicada:"
grep -c "PRODUCT_BUNDLE_IDENTIFIER = \"$NOVO_ID" ownCloud.xcodeproj/project.pbxproj | sed 's/^/  bundle ids NBN no projeto: /'
grep -rl "$ANTIGO_GRUPO<" "ownCloud File Provider" "ownCloud File Provider UI" "ownCloud Intents" \
	"ownCloud Share Extension" "ownCloud Action Extension" 2>/dev/null | sed 's/^/  AINDA com o grupo antigo: /' || true
