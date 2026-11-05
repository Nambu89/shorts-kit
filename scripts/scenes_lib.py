"""Piezas para montar las escenas de un Short en HyperFrames (vertical 1080×1920).

Cada escena es un archivo compositions/<id>.html con su propia línea de tiempo de GSAP.
Tu script de escenas importa esto, llama a configurar() y escribe cada escena con write().
Mira examples/demo/escenas.py para un ejemplo completo.

Reglas aprendidas (si no las sigues, `npm run check` o el render fallan o se ve mal):
- Ids únicos en todo el Short: nada de dos #s4-h2 aunque estén en escenas distintas.
- No animes `x` en un elemento que ya tenga transform en el CSS: GSAP lo pisa. Usa chip(), que centra sin transform.
- Para animar algo que ya se ha animado antes en la misma escena, usa immediateRender: false (lo hace pulse()).
- El primer fotograma tiene que tener algo en pantalla: es la portada por defecto.
- Textos de 28 px como mínimo: en el móvil, menos no se lee.
"""
from pathlib import Path

# ---------- paleta (cámbiala a la tuya) ----------
BG, CREAM, INK = "#0E1525", "#F5F3EE", "#111827"
BLUE, ORANGE, TEAL, MUTED, LINE = "#2B59C3", "#FFB347", "#0F766E", "#9CA3AF", "#33415C"

CFG = {"proyecto": Path("."), "escenas": [], "total": 0.0, "titulo": "Short"}


def configurar(proyecto, escenas, total, titulo):
	"""escenas: [(id, inicio, duración), ...] en segundos, sacados de los tramos de la voz."""
	CFG.update(proyecto=Path(proyecto), escenas=escenas, total=total, titulo=titulo)
	(CFG["proyecto"] / "compositions").mkdir(parents=True, exist_ok=True)


FONT = """
	@font-face { font-family: "Bricolage Grotesque"; font-weight: 800; src: url("assets/fonts/bricolage-grotesque-latin-800-normal.woff2") format("woff2"); }
	@font-face { font-family: Inter; font-weight: 700; src: url("assets/fonts/inter-latin-700-normal.woff2") format("woff2"); }
	@font-face { font-family: Inter; font-weight: 800; src: url("assets/fonts/inter-latin-800-normal.woff2") format("woff2"); }"""


def base_css(s):
	return f"""
	#root {{ position: absolute; inset: 0; background: {BG}; color: {CREAM}; font-family: Inter, sans-serif; overflow: hidden; }}
	#{s}-wrap {{ position: absolute; inset: 0; }}
	#{s}-wrap svg.lines {{ position: absolute; left: 0; top: 0; }}
	#{s}-wrap .kick {{ position: absolute; left: 90px; top: 222px; padding: 10px 22px; border-radius: 999px; background: {CREAM}; color: {INK}; font-size: 28px; font-weight: 800; letter-spacing: 3px; }}
	#{s}-wrap h2 {{ position: absolute; left: 90px; right: 90px; top: 290px; margin: 0; font-family: "Bricolage Grotesque", sans-serif; font-weight: 800; font-size: 92px; line-height: 1; letter-spacing: -2px; white-space: nowrap; }}
	#{s}-wrap .tool {{ position: absolute; border-radius: 28px; background: {CREAM}; display: grid; place-items: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4); }}
	#{s}-wrap .tool img {{ width: 56%; height: 56%; }}
	#{s}-wrap .tl {{ position: absolute; width: 220px; text-align: center; font-size: 28px; font-weight: 700; color: {CREAM}; }}
	#{s}-wrap .pill {{ position: absolute; left: 0; top: 0; width: 44px; height: 26px; border-radius: 13px; background: {ORANGE}; box-shadow: 0 0 22px rgba(255, 179, 71, 0.85); opacity: 0; }}
	#{s}-wrap .chip {{ position: absolute; padding: 10px 22px; border-radius: 999px; font-size: 30px; font-weight: 800; white-space: nowrap; }}"""


def write(s, dur, css, body, js):
	"""Escribe compositions/<s>.html."""
	html = f"""<template>
	<style>{FONT}{base_css(s)}{css}
	</style>
	<div id="root" data-composition-id="{s}" data-width="1080" data-height="1920">
		<div id="{s}-wrap" class="clip" data-start="0" data-duration="{dur}">{body}
		</div>
	</div>
	<script>
	const tl = gsap.timeline({{ paused: true }});{js}
	window.__timelines["{s}"] = tl;
	</script>
</template>
"""
	(CFG["proyecto"] / "compositions" / f"{s}.html").write_text(html, encoding="utf-8")


def index():
	"""Escribe index.html con las escenas, los subtítulos y la voz. No lo pisa si ya tiene efectos."""
	scenes = "".join(
		f'\n\t\t<div id="{s}" data-composition-id="{s}" data-composition-src="compositions/{s}.html" data-start="{st}" data-duration="{d}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>'
		for s, st, d in CFG["escenas"]
	)
	total = CFG["total"]
	html = f"""<!doctype html>
<html lang="es">
<head>
	<meta charset="UTF-8" />
	<meta name="viewport" content="width=1080, height=1920" />
	<title>{CFG["titulo"]}</title>
	<script src="assets/vendor/gsap.min.js"></script>
	<script src="assets/vendor/TextPlugin.min.js"></script>
	<script>gsap.registerPlugin(TextPlugin);</script>
	<style>
		* {{ margin: 0; padding: 0; box-sizing: border-box; }}
		html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: {BG}; }}
		#root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
	</style>
</head>
<body>
	<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">{scenes}
		<div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{total}" data-track-index="2" data-track-kind="captions" data-width="1080" data-height="1920"></div>
		<audio id="voz" class="clip" src="assets/voz.wav" data-start="0" data-track-index="3" data-volume="1"></audio>
	</div>
	<script>
		window.__timelines["main"] = gsap.timeline({{ paused: true }});
	</script>
</body>
</html>
"""
	idx = CFG["proyecto"] / "index.html"
	if idx.exists() and "sfx0" in idx.read_text(encoding="utf-8"):
		return
	idx.write_text(html, encoding="utf-8")


# ---------- piezas (devuelven HTML) ----------
def tool(i, cx, cy, icon, label=None, size=112):
	"""Tarjeta cuadrada con un icono de assets/icons/<icon>.svg, centrada en (cx, cy)."""
	h = f'\n\t\t\t<div class="tool" id="{i}" style="left:{cx - size // 2}px;top:{cy - size // 2}px;width:{size}px;height:{size}px"><img src="assets/icons/{icon}.svg" alt="" /></div>'
	if label:
		h += f'\n\t\t\t<div class="tl" id="{i}-l" style="left:{cx - 110}px;top:{cy + size // 2 + 12}px">{label}</div>'
	return h


def chip(i, x, y, text, bg=ORANGE, fg=INK, size=30, center=True):
	"""Etiqueta redondeada. Con center=True se centra en x sin usar transform."""
	inner = f"position:relative;display:inline-block;background:{bg};color:{fg};font-size:{size}px"
	if center:
		return f'\n\t\t\t<div style="position:absolute;left:{x - 470}px;width:940px;top:{y}px;text-align:center"><div class="chip" id="{i}" style="{inner}">{text}</div></div>'
	return f'\n\t\t\t<div class="chip" id="{i}" style="top:{y}px;left:{x}px;background:{bg};color:{fg};font-size:{size}px">{text}</div>'


def svg_lines(s, lines, color=LINE, w=6):
	"""Líneas [(x1, y1, x2, y2), ...] con ids <s>-ln0, <s>-ln1… para dibujarlas con draw_lines()."""
	out = '\n\t\t\t<svg class="lines" width="1080" height="1920" viewBox="0 0 1080 1920">'
	for i, (x1, y1, x2, y2) in enumerate(lines):
		out += f'<line id="{s}-ln{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}" stroke-linecap="round" />'
	return out + "</svg>"


def heading(s, kick, title, t_kick=0.05, t_title=0.15, color=CREAM, size=92):
	"""Antetítulo (kick) y título de la escena. Devuelve (html, js). Si el check dice que se sale, baja size."""
	body = f'\n\t\t\t<div class="kick" id="{s}-kick">{kick}</div>' if kick else ""
	body += f'\n\t\t\t<h2 id="{s}-h2" style="color:{color};font-size:{size}px">{title}</h2>'
	js = (rise(f"#{s}-kick", t_kick, 0.35) if kick else "") + rise(f"#{s}-h2", t_title)
	return body, js


# ---------- animaciones (devuelven JS para la línea de tiempo de la escena) ----------
def pop(sel, t, d=0.35):
	return f'\n\ttl.fromTo("{sel}", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: {d}, ease: "back.out(2.2)" }}, {t:.2f});'


def rise(sel, t, d=0.45):
	return f'\n\ttl.fromTo("{sel}", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: {d}, ease: "power3.out" }}, {t:.2f});'


def fade_out(sel, t, d=0.3):
	return f'\n\ttl.to("{sel}", {{ opacity: 0, duration: {d}, ease: "power1.in" }}, {t:.2f});'


def pulse(sel, t, k=1.12):
	return f'\n\ttl.fromTo("{sel}", {{ scale: 1 }}, {{ scale: {k}, duration: 0.18, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }}, {t:.2f});'


def draw_lines(s, lines, t, step=0.08, d=0.4):
	js = ""
	for i, (x1, y1, x2, y2) in enumerate(lines):
		ln = round(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
		js += f'\n\ttl.fromTo("#{s}-ln{i}", {{ attr: {{ "stroke-dasharray": "{ln} {ln}", "stroke-dashoffset": {ln} }} }}, {{ attr: {{ "stroke-dashoffset": 0 }}, duration: {d}, ease: "power2.out" }}, {t + i * step:.2f});'
	return js


def travel(sel, a, b, t, d=0.35):
	"""Una pastilla (.pill) viaja de a=(x, y) a b=(x, y): datos que pasan de un sitio a otro."""
	ax, ay = a
	bx, by = b
	return (
		f'\n\ttl.set("{sel}", {{ x: {ax - 22}, y: {ay - 13}, opacity: 1 }}, {t:.2f});'
		f'\n\ttl.to("{sel}", {{ x: {bx - 22}, y: {by - 13}, duration: {d}, ease: "power1.inOut" }}, {t:.2f});'
		f'\n\ttl.set("{sel}", {{ opacity: 0 }}, {t + d:.2f});'
	)


def typewrite(sel, text, t, d=0.5):
	"""Escribe el texto letra a letra (TextPlugin)."""
	return f'\n\ttl.to("{sel}", {{ text: "{text}", duration: {d}, ease: "none" }}, {t:.2f});'
