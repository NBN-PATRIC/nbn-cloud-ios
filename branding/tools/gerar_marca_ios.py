"""Gera as imagens da marca NBN Cloud do app iOS a partir do logo da NBN (logo-nbn.jpg).

Uso:  python3 branding/tools/gerar_marca_ios.py      (no Windows: py -3 ...)
Saída:
  ownCloud/Resources/Theming/branding-assets/        pasta que o build usa no lugar do tema do ownCloud
    branding-icon.png                   ícone 1024 (base do AppIcon; o build não o copia para o app)
    branding-logo.png                   logo das telas de marca (cadastro de conta e barra lateral)
    branding-background.png             fundo das telas de marca
    branding-splashscreen-logo.png      logo da abertura
    branding-splashscreen-background.png  cor de fundo da abertura (1 x 1)
  ownCloud/Resources/Assets.xcassets/AppIcon.appiconset/branding-icon-<n>x<n>.png
  branding/tools/preview.png            folha de conferência (não vai para o build)

Mesmo desenho do NBN Cloud Android (nbn-cloud-android/branding/tools/gerar_marca.py) e desktop. Só depende do
Pillow; a fonte do "Cloud" é a Segoe UI Semibold (Windows) ou, na falta dela, a DejaVu Sans Bold.
"""
import pathlib

from PIL import Image, ImageDraw, ImageFont

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
ASSETS = RAIZ / 'ownCloud' / 'Resources' / 'Theming' / 'branding-assets'
APPICON = RAIZ / 'ownCloud' / 'Resources' / 'Assets.xcassets' / 'AppIcon.appiconset'
LOGO = AQUI / 'logo-nbn.jpg'
FONTES = [r'C:\Windows\Fonts\seguisb.ttf', '/System/Library/Fonts/SFNS.ttf', 'DejaVuSans-Bold.ttf']

S = 1024
NAVY = (31, 42, 68, 255)           # #1F2A44, cor do timbrado
AZUL_CLARO = (143, 179, 240, 255)  # #8FB3F0, "Cloud" sobre o azul-marinho
BRANCO = (255, 255, 255, 255)
TAM_APPICON = [20, 29, 40, 58, 60, 76, 80, 87, 120, 152, 167, 180, 1024]


def fonte(tamanho):
    for f in FONTES:
        try:
            return ImageFont.truetype(f, tamanho)
        except OSError:
            continue
    raise SystemExit('nenhuma fonte encontrada para o "Cloud"')


def circulo(d, cx, cy, r, cor):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=cor)


def nuvem(cor, caixa, lado=S):
    """Nuvem (círculos + retângulo arredondado) dentro de caixa=(x0, y0, x1, y1) em fração do lado."""
    x0, y0, x1, y1 = caixa
    w, h = (x1 - x0) * lado, (y1 - y0) * lado
    ox, oy = x0 * lado, y0 * lado
    camada = Image.new('RGBA', (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    d.rounded_rectangle([ox, oy + 0.48 * h, ox + w, oy + h], radius=0.26 * h, fill=cor)
    circulo(d, ox + 0.30 * w, oy + 0.58 * h, 0.30 * h, cor)
    circulo(d, ox + 0.54 * w, oy + 0.42 * h, 0.42 * h, cor)
    circulo(d, ox + 0.78 * w, oy + 0.64 * h, 0.26 * h, cor)
    return camada


def mascara_logo(com_telecom=True):
    """Máscara (L) das letras do logo; sem "telecom" e sem o sorriso quando com_telecom=False."""
    im = Image.open(LOGO).convert('L')
    if not com_telecom:
        im = im.crop((0, 6, im.width, 182))
    m = im.point(lambda v: 255 if v < 110 else (0 if v > 200 else int((200 - v) * 255 / 90)))
    return m.crop(m.getbbox())


def pintar(mascara, cor, largura):
    alt = round(mascara.height * largura / mascara.width)
    m = mascara.resize((round(largura), alt), Image.LANCZOS)
    img = Image.new('RGBA', m.size, cor)
    img.putalpha(m)
    return img


def icone_app():
    """Ícone do iOS: quadrado cheio (o sistema arredonda os cantos), sem transparência."""
    img = Image.new('RGBA', (S, S), NAVY)
    img.alpha_composite(nuvem(BRANCO, (0.13, 0.22, 0.87, 0.78)))
    letras = pintar(mascara_logo(False), NAVY, 0.44 * S)
    img.alpha_composite(letras, (round(0.52 * S - letras.width / 2), round(0.60 * S - letras.height / 2)))
    return img.convert('RGB')


def logo_horizontal(cor_logo, cor_cloud, alt_px):
    """Logo "nbn telecom" + "Cloud" lado a lado, com alt_px de altura total."""
    escala = 2
    H = alt_px * escala
    proporcao = mascara_logo(True)
    lw = round(H * proporcao.width / proporcao.height)
    logo = pintar(proporcao, cor_logo, lw)
    f = fonte(round(H * 0.62))
    caixa = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textbbox((0, 0), 'Cloud', font=f)
    tw = caixa[2] - caixa[0]
    vao = round(H * 0.14)
    img = Image.new('RGBA', (lw + vao + tw, H), (0, 0, 0, 0))
    img.alpha_composite(logo, (0, 0))
    # "Cloud" alinhado à linha de base das letras "nbn" (60% da altura do logo)
    ImageDraw.Draw(img).text((lw + vao - caixa[0], round(H * 0.60) - caixa[3]), 'Cloud', font=f, fill=cor_cloud)
    img = img.crop(img.getbbox())
    return img.resize((round(img.width / escala), round(img.height / escala)), Image.LANCZOS)


def enquadrar(img, W, H, margem=0.0):
    """Centraliza img numa tela transparente W x H, com margem (fração) e reduzindo se precisar."""
    w, h = W * (1 - 2 * margem), H * (1 - 2 * margem)
    f = min(w / img.width, h / img.height)
    img = img.resize((round(img.width * f), round(img.height * f)), Image.LANCZOS)
    tela = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    tela.alpha_composite(img, ((W - img.width) // 2, (H - img.height) // 2))
    return tela


def fundo(W=1280, H=1920):
    img = Image.new('RGBA', (W, H), NAVY)
    for (x0, y0, lado_f, alfa) in ((0.45, -0.05, 0.85, 26), (-0.35, 0.68, 0.80, 18)):
        lado = round(lado_f * W)
        img.alpha_composite(nuvem((143, 179, 240, alfa), (0, 0, 1, 1), lado), (round(x0 * W), round(y0 * H)))
    return img.convert('RGB')


def salvar(img, caminho):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    img.save(caminho, optimize=True)


def main():
    icone = icone_app()
    salvar(icone, ASSETS / 'branding-icon.png')
    for t in TAM_APPICON:
        salvar(icone.resize((t, t), Image.LANCZOS), APPICON / f'branding-icon-{t}x{t}.png')

    claro = logo_horizontal(BRANCO, AZUL_CLARO, 700)
    # telas de marca (cadastro e barra lateral, caixa de 128 x 64 pt): logo justo, sem sobra
    salvar(enquadrar(claro, 2048, round(2048 * claro.height / claro.width) + 80, margem=0.0), ASSETS / 'branding-logo.png')
    # abertura: tela quadrada como a do ownCloud (o storyboard usa 2048 x 2048, aspect fit)
    salvar(enquadrar(claro, 2048, 2048, margem=0.02), ASSETS / 'branding-splashscreen-logo.png')
    salvar(Image.new('RGB', (1, 1), NAVY[:3]), ASSETS / 'branding-splashscreen-background.png')
    salvar(fundo(), ASSETS / 'branding-background.png')

    # folha de conferência
    folha = Image.new('RGBA', (1240, 720), (240, 240, 240, 255))
    d = ImageDraw.Draw(folha)
    ic = icone.convert('RGBA').resize((180, 180), Image.LANCZOS)
    mascara = Image.new('L', (180, 180), 0)
    ImageDraw.Draw(mascara).rounded_rectangle([0, 0, 179, 179], radius=40, fill=255)
    folha.paste(ic, (20, 20), mascara)
    x = 220
    for t in (87, 60, 40, 29, 20):
        folha.alpha_composite(icone.convert('RGBA').resize((t, t), Image.LANCZOS), (x, 20)); x += t + 16
    fd = fundo().convert('RGBA').resize((320, 480))
    lg = Image.open(ASSETS / 'branding-logo.png')
    lg.thumbnail((280, 140))
    fd.alpha_composite(lg, ((320 - lg.width) // 2, 120))
    folha.alpha_composite(fd, (20, 220))
    sp = Image.new('RGBA', (320, 480), NAVY)
    sl = Image.open(ASSETS / 'branding-splashscreen-logo.png')
    sl.thumbnail((240, 240))
    sp.alpha_composite(sl, ((320 - sl.width) // 2, (480 - sl.height) // 2))
    folha.alpha_composite(sp, (360, 220))
    barra = Image.new('RGBA', (300, 120), NAVY)
    lb = Image.open(ASSETS / 'branding-logo.png')
    lb.thumbnail((128, 64))
    barra.alpha_composite(lb, ((300 - lb.width) // 2, (120 - lb.height) // 2))
    folha.alpha_composite(barra, (720, 220))
    d.text((720, 350), 'barra lateral (128 x 64 pt)', fill=(0, 0, 0, 255))
    salvar(folha, AQUI / 'preview.png')
    print('ok:', ASSETS)


if __name__ == '__main__':
    main()
