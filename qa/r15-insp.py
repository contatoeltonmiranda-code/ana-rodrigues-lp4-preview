# -*- coding: utf-8 -*-
# r15 item 1 — reproduzir o crop do Elton (ref 34): renderizar o hero em 4 larguras,
# medir altura do .hero vs altura natural do cover e capturar provas "antes".
import sys, os
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8931"
SAIDA = os.path.join(os.path.dirname(__file__), "provas")
os.makedirs(SAIDA, exist_ok=True)
LARGURAS = [1440, 1024, 768, 390]

with sync_playwright() as p:
    nav = p.chromium.launch()
    for largura in LARGURAS:
        ctx = nav.new_context(viewport={"width": largura, "height": 900}, device_scale_factor=1)
        pg = ctx.new_page()
        pg.goto(BASE + "/", wait_until="networkidle")
        pg.wait_for_timeout(400)
        m = pg.evaluate("""() => {
          const h = document.querySelector('.hero');
          const r = h.getBoundingClientRect();
          const cs = getComputedStyle(h, '::after');
          const img = new Image(); img.src = getComputedStyle(h,'::after').backgroundImage.match(/url\\("?([^")]+)"?\\)/)[1];
          return {w: r.width, heroH: Math.round(r.height),
                  ratioImg: img.naturalWidth/img.naturalHeight,
                  natW: img.naturalWidth, natH: img.naturalHeight,
                  pos: cs.backgroundPosition, size: cs.backgroundSize};
        }""")
        cover_h = m["w"] / m["ratioImg"]
        print(f"{largura}px: hero {m['w']:.0f}x{m['heroH']}px | img {m['natW']}x{m['natH']} "
              f"(ratio {m['ratioImg']:.3f}) | cover usaria {cover_h:.0f}px de altura | "
              f"zoom = {m['heroH']/cover_h:.2f}x | pos={m['pos']} size={m['size']}")
        pg.locator(".hero").first.screenshot(path=os.path.join(SAIDA, f"antes-hero-{largura}.png"))
        ctx.close()
    nav.close()
print("provas em", SAIDA)