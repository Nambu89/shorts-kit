"""Ejemplo mínimo: dos escenas (gancho y cierre) para probar que todo funciona.

Desde la raíz del kit:
	python scripts/nuevo_proyecto.py ../short-demo
	(pon un audio en ../short-demo/assets/voz.wav, vale cualquiera de unos 12 s)
	python examples/demo/escenas.py ../short-demo
	python scripts/captions_build.py examples/demo/tramos.json examples/demo/textos.json ../short-demo "#FFB347" 12
	cd ../short-demo && npm run check && npm run render
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from scenes_lib import (BLUE, INK, ORANGE, chip, configurar, draw_lines, heading, index, pop, pulse,  # noqa: E402
	svg_lines, tool, travel, write)

ESCENAS = [("s1", 0.0, 6.0), ("s2", 6.0, 6.0)]
TOTAL = 12.0


def s1():
	"""Gancho: los datos viajan de la tabla al informe."""
	s, dur = "s1", 6.0
	body, js = heading(s, "POWER BI", "¿Import o DirectQuery?", size=80)
	lines = [(300, 760, 780, 760)]
	body += svg_lines(s, lines)
	body += tool("s1-a", 240, 760, "tabla", "Origen", 150)
	body += tool("s1-b", 840, 760, "grafico", "Informe", 150)
	body += '\n\t\t\t<div class="pill" id="s1-p"></div>'
	body += chip("s1-q", 540, 1000, "¿Copio los datos o los consulto?", BLUE, "#FFFFFF", 36)
	js += pop("#s1-a", 0.4) + pop("#s1-b", 0.7) + draw_lines(s, lines, 1.0)
	js += travel("#s1-p", (320, 760), (760, 760), 1.6) + travel("#s1-p", (320, 760), (760, 760), 2.2)
	js += pop("#s1-q", 3.0) + pulse("#s1-q", 4.5, 1.06)
	write(s, dur, "", body, js)


def s2():
	"""Cierre: la URL de la guía, siempre la misma."""
	s, dur = "s2", 6.0
	body, js = heading(s, "", "Guía gratis")
	body += '\n\t\t\t<div id="s2-url">tuweb.dev/guias</div>'
	css = f"""
	#s2-url {{ position: absolute; left: 90px; right: 90px; top: 700px; height: 124px; border-radius: 30px; background: {ORANGE}; color: {INK}; display: grid; place-items: center; font-family: "Bricolage Grotesque", sans-serif; font-weight: 800; font-size: 56px; opacity: 0; }}"""
	js += pop("#s2-url", 0.8) + pulse("#s2-url", 2.0, 1.05)
	write(s, dur, css, body, js)


if __name__ == "__main__":
	configurar(sys.argv[1], ESCENAS, TOTAL, "Short de ejemplo")
	for f in (s1, s2, index):
		f()
	print("escenas listas")
