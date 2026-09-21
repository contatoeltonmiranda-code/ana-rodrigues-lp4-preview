"""r17-insp — provas e inspecao da rodada 17 (LP 4 Ana Rodrigues).

Itens verificados:
  1. rodape sem links de checkout (so 3 links legais)
  2. passos como CARDS com borda conic ANIMADA (2 frames da mesma regiao
     diferem = borda rodando)
  3. fontes Cinzel (titulos) / Montserrat (corpo) computadas; dourado
     #C29A5E / #dcbb86 nos discos e botoes dos planos
  4. ambos os planos com botao dourado + item "Todos os bonus..."
  5. .cta-mini com 3 mini-itens sob o CTA do hero

Provas: screenshots antes (backup r16, servido em 8933) e depois (8931)
+ lado a lado em _ajustes/rodada-17/provas/.
Uso: python qa/r17-insp.py
"""
import json
import os
import shutil
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # raiz projeto
PREVIEW = os.path.join(RAIZ, "preview")
PROVAS = os.path.join(RAIZ, "_ajustes", "rodada-17", "provas")
ANTES_DIR = os.path.join(PROVAS, "antes")
PORT_DEPOIS, PORT_ANTES = 8931, 8933

# ---------------------------------------------------------------- montar ANTES
os.makedirs(ANTES_DIR, exist_ok=True)
shutil.copy(os.path.join(PREVIEW, "index.html.bak-r16"),
            os.path.join(ANTES_DIR, "index.html"))
assets_dst = os.path.join(ANTES_DIR, "assets")
if os.path.isdir(assets_dst):
    shutil.rmtree(assets_dst)
shutil.copytree(os.path.join(PREVIEW, "assets"), assets_dst)
shutil.copy(os.path.join(PREVIEW, "assets", "style.css.bak-r16"),
            os.path.join(assets_dst, "style.css"))

servidores = []
for porta, pasta in [(PORT_DEPOIS, PREVIEW), (PORT_ANTES, ANTES_DIR)]:
    pr = subprocess.Popen([sys.executable, "-m", "http.server", str(porta)],
                          cwd=pasta, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    servidores.append(pr)
time.sleep(1.2)

SECOES = [(".hero", "hero"), (".caminho-wrap", "caminho"),
          (".sec-preco", "preco"), ("footer", "footer")]

relatorio = {}

with sync_playwright() as p:
    nav = p.chromium.launch()

    for rotulo, porta in [("antes", PORT_ANTES), ("depois", PORT_DEPOIS)]:
        ctx = nav.new_context(viewport={"width": 1440, "height": 900},
                              device_scale_factor=1)
        pg = ctx.new_page()
        pg.goto(f"http://127.0.0.1:{porta}/", wait_until="networkidle")
        pg.wait_for_timeout(1200)

        if rotulo == "depois":
            dados = pg.evaluate("""() => {
              const gs = el => el ? getComputedStyle(el) : null;
              const h2 = document.querySelector('.sec-func h2');
              const h3 = document.querySelector('.no-corpo h3');
              const p = document.querySelector('.no-corpo p');
              const btn = document.querySelector('.hero .btn');
              const ck = document.querySelector('.plano-inc li .ck');
              const planoBtnE = document.querySelector('.plano.essenza .btn');
              const planoBtnS = document.querySelector('.plano.sapori .btn');
              const noCard = document.querySelector('.no');
              const mini = document.querySelectorAll('.cta-mini li');
              const discos = Array.from(document.querySelectorAll('.plano-inc li .ck'))
                .slice(0,1).map(e=>gs(e).backgroundImage);
              const bonus = Array.from(document.querySelectorAll('.plano-inc .feat'))
                .map(e=>e.textContent.trim())
                .filter(t=>t.startsWith('Todos os b'));
              const foot = Array.from(document.querySelectorAll('.foot-links a')).map(a=>a.textContent.trim());
              return {
                h2Fonte: gs(h2).fontFamily, h2Peso: gs(h2).fontWeight,
                h3Fonte: gs(h3).fontFamily,
                corpoFonte: gs(p).fontFamily,
                btnFonte: gs(btn).fontFamily, btnPeso: gs(btn).fontWeight,
                ckBg: gs(ck).backgroundImage,
                btnEssenzaBg: gs(planoBtnE).backgroundImage,
                btnSaporiBg: gs(planoBtnS).backgroundImage,
                btnEssenzaCor: gs(planoBtnE).color,
                noBg: gs(noCard).borderRadius,
                noBefore: gs(noCard,'::before').backgroundImage.slice(0,80),
                miniItens: mini.length,
                miniTxt: Array.from(mini).map(l=>l.textContent.trim()),
                bonusCount: bonus.length,
                footerLinks: foot
              };
            }""")
            relatorio["inspecao"] = dados

        for seletor, nome in SECOES:
            loc = pg.locator(seletor).first
            loc.scroll_into_view_if_needed()
            pg.wait_for_timeout(500)
            loc.screenshot(path=os.path.join(PROVAS, f"r17-{nome}-{rotulo}-1440.png"))

        # animacao da borda: 2 frames da mesma regiao de um card
        card = pg.locator(".no").first
        card.scroll_into_view_if_needed()
        pg.wait_for_timeout(400)
        f1 = os.path.join(PROVAS, f"r17-anim-f1-{rotulo}.png")
        card.screenshot(path=f1)
        pg.wait_for_timeout(900)
        f2 = os.path.join(PROVAS, f"r17-anim-f2-{rotulo}.png")
        card.screenshot(path=f2)

        # mobile 390: caminho + preco + hero
        ctx.close()
        ctx = nav.new_context(viewport={"width": 390, "height": 844},
                              device_scale_factor=1)
        pg = ctx.new_page()
        pg.goto(f"http://127.0.0.1:{porta}/", wait_until="networkidle")
        pg.wait_for_timeout(1200)
        for seletor, nome in SECOES:
            loc = pg.locator(seletor).first
            loc.scroll_into_view_if_needed()
            pg.wait_for_timeout(400)
            loc.screenshot(path=os.path.join(PROVAS, f"r17-{nome}-{rotulo}-390.png"))
        ov = pg.evaluate("Math.max(0,document.documentElement.scrollWidth-window.innerWidth)")
        relatorio[f"overflow-390-{rotulo}"] = ov
        ctx.close()
    nav.close()

for pr in servidores:
    pr.terminate()

# ------------------------------------------------------------- comparar frames
try:
    from PIL import Image, ImageChops
    for rotulo in ("antes", "depois"):
        a = Image.open(os.path.join(PROVAS, f"r17-anim-f1-{rotulo}.png")).convert("RGB")
        b = Image.open(os.path.join(PROVAS, f"r17-anim-f2-{rotulo}.png")).convert("RGB")
        diff = ImageChops.difference(a, b)
        bbox = diff.getbbox()
        px = sum(1 for v in diff.getdata() if sum(v) > 12)
        relatorio[f"borda-animada-{rotulo}"] = {
            "bbox_diff": bbox, "pixels_diferentes": px}
except ImportError:
    relatorio["borda-animada"] = "PIL indisponivel"

# ------------------------------------------------------- lado a lado (provas)
try:
    from PIL import Image
    for nome in ("hero", "caminho", "preco", "footer"):
        for vp in ("1440", "390"):
            try:
                a = Image.open(os.path.join(PROVAS, f"r17-{nome}-antes-{vp}.png"))
                b = Image.open(os.path.join(PROVAS, f"r17-{nome}-depois-{vp}.png"))
                h = max(a.height, b.height)
                comp = Image.new("RGB", (a.width + b.width + 16, h), "#222")
                comp.paste(a, (0, 0)); comp.paste(b, (a.width + 16, 0))
                comp.save(os.path.join(PROVAS, f"r17-vs-{nome}-{vp}.png"))
            except FileNotFoundError:
                pass
except ImportError:
    pass

json.dump(relatorio, open(os.path.join(PREVIEW, "qa", "r17-insp.json"), "w",
                          encoding="utf-8"), indent=2, ensure_ascii=False)
print(json.dumps(relatorio, indent=2, ensure_ascii=False))