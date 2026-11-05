"""Genera compositions/captions.html (subtítulos palabra a palabra) para un Short.

Tiempos: cada tramo de voz (inicio/fin medidos con silencedetect + Whisper) se reparte entre
sus palabras según su longitud hablada aproximada. Los textos son los del guion, corregidos
con lo que realmente se dijo.

Uso: python captions_build.py <tramos.json> <textos.json> <proyecto> <color_activo> <duracion>
"""
import json
import re
import sys
from pathlib import Path

# Palabras cortas por escrito pero largas al decirlas. Añade aquí las de tu tema
PESO = {"BI": 7, "DAX": 6, "KPI": 9, "SQL": 8, "ETL": 8, "OneLake": 9, "LangGraph": 10, "CPU": 9, "Workspaces": 12, "Playwright": 10, "365": 14, "GPU": 7, "202": 12, "MCP": 8, "API": 6, "DNI": 8, "QR": 6, "OpenAPI": 9, "operationId": 12}
MAX_PAL = 4


def peso(p):
	limpio = re.sub(r"[^\wáéíóúüñÁÉÍÓÚÜÑ]", "", p)
	return PESO.get(limpio, len(limpio) + 2)


def palabras_con_tiempo(tramos, textos):
	out = []
	for tr, txt in zip(tramos, textos):
		ps = txt.split()
		pesos = [peso(p) for p in ps]
		total = sum(pesos)
		a, b = tr["start"] + 0.03, tr["end"]
		t = a
		for p, w in zip(ps, pesos):
			d = (b - a) * w / total
			out.append({"text": p, "start": round(t, 3), "end": round(t + d, 3), "tramo": len(out) and tr["start"]})
			t += d
		out[-1]["fin_tramo"] = True
	return out


def grupos(ws):
	gs, cur = [], []
	for w in ws:
		if cur and len(" ".join(x["text"] for x in cur + [w])) > 26:
			gs.append(cur)
			cur = []
		cur.append(w)
		corte = w.get("fin_tramo") or w["text"][-1] in ".,:;?" or len(cur) >= MAX_PAL
		if corte:
			gs.append(cur)
			cur = []
	if cur:
		gs.append(cur)
	return gs


def main(tramos_p, textos_p, proyecto, activo, dur):
	tramos = json.load(open(tramos_p, encoding="utf-8"))
	textos = json.load(open(textos_p, encoding="utf-8"))
	assert len(tramos) == len(textos), (len(tramos), len(textos))
	ws = palabras_con_tiempo(tramos, textos)
	gs = grupos(ws)
	html_g, js = [], []
	for gi, g in enumerate(gs):
		ini = max(0.1, g[0]["start"] - 0.05)
		sig = gs[gi + 1][0]["start"] - 0.05 if gi + 1 < len(gs) else float(dur) - 0.05
		fin = min(g[-1]["end"] + 0.35, sig)
		spans = " ".join(f'<span id="w{gi}_{wi}">{w["text"]}</span>' for wi, w in enumerate(g))
		html_g.append(f'\t\t\t<div class="cg" id="g{gi}"><div class="pill">{spans}</div></div>')
		js.append(f'\ttl.set("#g{gi}", {{ opacity: 1, visibility: "visible" }}, {ini:.3f});')
		js.append(f'\ttl.fromTo("#g{gi} .pill", {{ y: 14, scale: 0.96 }}, {{ y: 0, scale: 1, duration: 0.14, ease: "power2.out" }}, {ini:.3f});')
		for wi, w in enumerate(g):
			# Se apaga cuando entra la siguiente palabra: nunca dos resaltadas a la vez
			apaga = g[wi + 1]["start"] if wi + 1 < len(g) else min(w["end"] + 0.25, fin)
			js.append(f'\ttl.set("#w{gi}_{wi}", {{ color: "{activo}" }}, {w["start"]:.3f});')
			js.append(f'\ttl.set("#w{gi}_{wi}", {{ color: "#FFFFFF" }}, {apaga:.3f});')
		js.append(f'\ttl.set("#g{gi}", {{ opacity: 0, visibility: "hidden" }}, {fin:.3f});')
	html = f"""<template>
	<style>
	#root {{ position: absolute; inset: 0; overflow: visible; }}
	#cap-wrap {{ position: absolute; inset: 0; }}
	#cap-wrap .cg {{ position: absolute; left: 0; right: 0; top: 1235px; text-align: center; opacity: 0; visibility: hidden; overflow: visible; }}
	#cap-wrap .pill {{ display: inline-block; max-width: 940px; padding: 14px 30px 18px; border-radius: 20px; background: rgba(11, 18, 32, 0.9); color: #FFFFFF; font-family: Inter, sans-serif; font-weight: 800; font-size: 52px; white-space: nowrap; line-height: 1.15; letter-spacing: -0.3px; }}
	</style>
	<div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
		<div id="cap-wrap" class="clip" data-start="0" data-duration="{dur}">
{chr(10).join(html_g)}
		</div>
	</div>
	<script>
	const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
	window.__timelines["captions"] = tl;
	</script>
</template>
"""
	Path(proyecto, "compositions", "captions.html").write_text(html, encoding="utf-8")
	json.dump(ws, open(Path(proyecto, "assets", "words.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
	print(f"{len(ws)} palabras, {len(gs)} grupos")


if __name__ == "__main__":
	main(*sys.argv[1:6])
