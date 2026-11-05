"""Genera la guía en PDF de un Short (páginas de 1080×1350, el formato de carrusel de LinkedIn).

Uso: python gen_guide.py contenido.py salida.pdf [carpeta_fuentes]

contenido.py define:
	TITULO, SUBTITULO, AUTOR, WEB, FUENTE, FECHA
	PAGINAS = [(kick, titulo, [bloques]), ...]   # de la 2 en adelante; la 1 es la portada
	Bloques: ("card", titulo, texto) · ("row", etiqueta, texto) · ("p", texto)

Mira ejemplo_contenido.py. Necesita: pip install playwright && playwright install chromium
carpeta_fuentes: la assets/fonts de cualquier Short creado con nuevo_proyecto.py. Sin ella usa las del sistema.
"""
import importlib.util
import sys
from pathlib import Path

CREAM, INK, BLUE, ORANGE, TEAL, CARD, SOFT = "#F5F3EE", "#111827", "#2B59C3", "#FFB347", "#0F766E", "#1F2937", "#CBD5E1"
ROW_COLORS = [ORANGE, BLUE, TEAL, INK]


def cargar(path):
	spec = importlib.util.spec_from_file_location("contenido", path)
	m = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(m)
	return m


def bloque(b, dark, k):
	sub = SOFT if dark else "#4B5563"
	if b[0] == "card":
		bg = CARD if dark else "#FFFFFF"
		return f"""<div style="flex-grow:1;border-radius:30px;background:{bg};padding:28px 38px;display:flex;flex-direction:column;gap:10px">
<p style="margin:0;font-size:40px;line-height:1.15;font-weight:700">{b[1]}</p>
<p style="margin:0;font-size:30px;line-height:1.35;color:{sub}">{b[2]}</p></div>"""
	if b[0] == "row":
		color = ROW_COLORS[k % len(ROW_COLORS)]
		return f"""<div style="display:flex;gap:26px;align-items:flex-start;padding:14px 0;border-bottom:2px solid {'#374151' if dark else '#D6D3CC'}">
<span style="flex-shrink:0;width:230px;padding:10px 0;border-radius:18px;background:{color};color:{INK if color == ORANGE else '#FFFFFF'};text-align:center;font-size:30px;font-weight:700">{b[1]}</span>
<p style="margin:0;font-size:30px;line-height:1.3;color:{sub}">{b[2]}</p></div>"""
	return f'<p style="margin:0;font-size:34px;line-height:1.35">{b[1]}</p>'


def page(i, n, dark, kick, title, bloques, fuente):
	bg, fg = (INK, CREAM) if dark else (CREAM, INK)
	kbg, kfg = (ORANGE, INK) if dark else (INK, CREAM)
	inner = "".join(bloque(b, dark, k) for k, b in enumerate(bloques))
	return f"""<section style="background:{bg};color:{fg}">
<div style="display:flex"><span style="padding:14px 26px;border-radius:999px;background:{kbg};color:{kfg};font-size:28px;font-weight:700;letter-spacing:2px">{kick}</span></div>
<h2 class="bg" style="margin:0;font-size:88px;line-height:0.98;letter-spacing:-2px">{title}</h2>
<div style="flex-grow:1;display:flex;flex-direction:column;gap:22px">{inner}</div>
<div style="display:flex;justify-content:space-between;padding-top:26px;border-top:3px solid {fg};font-size:26px;font-weight:700">
<span>Fuente: {fuente}</span><span>{i}/{n}</span></div></section>"""


def portada(c):
	return f"""<section style="background:{CREAM};color:{INK}">
<div style="display:flex"><span style="padding:14px 26px;border-radius:999px;background:{INK};color:{CREAM};font-size:26px;font-weight:700;letter-spacing:3px">GUÍA PARA GUARDAR</span></div>
<div style="flex-grow:1;display:flex;flex-direction:column;justify-content:flex-end;gap:40px">
<h1 class="bg" style="margin:0;font-size:132px;line-height:0.95;letter-spacing:-2.5px">{c.TITULO}</h1>
<p style="margin:0;font-size:40px;line-height:1.3;font-weight:500;max-width:880px">{c.SUBTITULO}</p></div>
<div style="display:flex;justify-content:space-between;margin-top:72px;padding-top:32px;border-top:3px solid {INK};font-size:28px;font-weight:700">
<span>{c.AUTOR}</span><span>{c.WEB}</span></div></section>"""


def html(c, fonts):
	n = len(c.PAGINAS) + 1
	paginas = [portada(c)] + [page(i, n, i % 2 == 0, *p, c.FUENTE) for i, p in enumerate(c.PAGINAS, 2)]
	ff = ""
	if fonts.exists():
		ff = "".join(f'@font-face{{font-family:"{fam}";font-weight:{w};src:url("{(fonts / f).as_uri()}")}}'
			for fam, w, f in [("Bricolage Grotesque", 800, "bricolage-grotesque-latin-800-normal.woff2"),
				("Inter", 700, "inter-latin-700-normal.woff2"), ("Inter", 800, "inter-latin-800-normal.woff2")] if (fonts / f).exists())
	return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{ff}
@page{{size:1080px 1350px;margin:0}} html,body{{margin:0;padding:0}}
section{{width:1080px;height:1350px;box-sizing:border-box;padding:88px 88px 72px;display:flex;flex-direction:column;gap:36px;font-family:Inter,system-ui,sans-serif;break-after:page;overflow:hidden}}
.bg{{font-family:'Bricolage Grotesque',sans-serif;font-weight:800}}
</style></head><body>{''.join(paginas)}</body></html>"""


def main(contenido, salida, fuentes=None):
	from playwright.sync_api import sync_playwright
	c = cargar(contenido)
	fonts = Path(fuentes or "no-hay-fuentes").resolve()
	tmp = Path(salida).with_suffix(".html")
	tmp.write_text(html(c, fonts), encoding="utf-8")
	with sync_playwright() as pw:
		b = pw.chromium.launch()
		pg = b.new_page(viewport={"width": 1080, "height": 1350})
		pg.goto(tmp.resolve().as_uri())
		pg.evaluate("document.fonts.ready")
		pg.pdf(path=salida, width="1080px", height="1350px", print_background=True)
		b.close()
	print(f"{salida}: {len(c.PAGINAS) + 1} páginas (el HTML queda en {tmp} para revisarlo)")


if __name__ == "__main__":
	main(*sys.argv[1:4])
