"""Crea la carpeta de un Short nuevo lista para HyperFrames.

Uso: python nuevo_proyecto.py <carpeta>

Hace esto:
- package.json con HyperFrames fijado a una versión probada, GSAP y las fuentes (@fontsource).
- npm install.
- Copia GSAP, TextPlugin y las fuentes a assets/ (el render no lee node_modules).
- Copia los iconos genéricos del kit a assets/icons/.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
HF = "hyperframes@0.8.191"
FUENTES = [
	("bricolage-grotesque", "bricolage-grotesque-latin-800-normal.woff2"),
	("inter", "inter-latin-700-normal.woff2"),
	("inter", "inter-latin-800-normal.woff2"),
]


def main(carpeta):
	p = Path(carpeta)
	for d in ("assets/vendor", "assets/fonts", "assets/icons", "assets/sfx", "compositions", "renders"):
		(p / d).mkdir(parents=True, exist_ok=True)
	pkg = {
		"name": p.name,
		"private": True,
		"type": "module",
		"scripts": {
			"dev": f"npx --yes {HF} preview",
			"check": f"npx --yes {HF} check",
			"render": f"npx --yes {HF} render",
		},
		"dependencies": {
			"@fontsource/bricolage-grotesque": "^5.3.0",
			"@fontsource/inter": "^5.3.0",
			"gsap": "^3.14.2",
		},
	}
	(p / "package.json").write_text(json.dumps(pkg, indent="\t") + "\n", encoding="utf-8")
	shutil.copy(KIT / "templates" / "hyperframes.json", p / "hyperframes.json")
	subprocess.run("npm install --no-audit --no-fund", cwd=p, shell=True, check=True)
	nm = p / "node_modules"
	shutil.copy(nm / "gsap" / "dist" / "gsap.min.js", p / "assets" / "vendor")
	shutil.copy(nm / "gsap" / "dist" / "TextPlugin.min.js", p / "assets" / "vendor")
	for pkg_name, f in FUENTES:
		shutil.copy(nm / "@fontsource" / pkg_name / "files" / f, p / "assets" / "fonts")
	for icon in (KIT / "assets" / "icons").glob("*.svg"):
		shutil.copy(icon, p / "assets" / "icons")
	print(f"Proyecto listo en {p}. Pon la voz en {p / 'assets' / 'voz.wav'}.")


if __name__ == "__main__":
	main(sys.argv[1])
