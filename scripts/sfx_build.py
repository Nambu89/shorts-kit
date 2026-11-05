"""Añade efectos de sonido (<audio>) al index.html de un Short.

Cada efecto se coloca para que su golpe (el pico de volumen) caiga un fotograma después de la imagen.
El pico y la duración de cada efecto se miden solos al leer el archivo.

Uso: python sfx_build.py <proyecto> <cues.json> [carpeta_efectos]
cues.json: [["nombre", tiempo_absoluto, volumen_opcional], ...]
carpeta_efectos: donde están tus <nombre>.mp3 (por defecto ./sfx o la variable SFX_DIR).

Se puede ejecutar varias veces: borra los efectos anteriores antes de insertar los nuevos.
"""
import json
import os
import re
import shutil
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

VOL = {"error": 0.9, "impact-bass-1": 0.3, "impact-bass-2": 0.3, "sparkle": 0.22, "click-soft": 0.28,
	"key-press": 0.35, "typing": 0.22, "glitch-3": 0.3, "whoosh": 0.3, "whoosh-short": 0.25}
FRAME = 1 / 30


def medir(path):
	"""Devuelve (segundo del pico, duración) de un archivo de audio."""
	audio, sr = sf.read(str(path), dtype="float32")
	if audio.ndim > 1:
		audio = np.abs(audio).max(axis=1)
	return float(np.argmax(np.abs(audio))) / sr, round(len(audio) / sr, 2)


def main(proyecto, cues_p, src=None):
	src = Path(src or os.environ.get("SFX_DIR", "sfx"))
	p = Path(proyecto)
	(p / "assets" / "sfx").mkdir(parents=True, exist_ok=True)
	cues = json.load(open(cues_p, encoding="utf-8"))
	medidas = {}
	fin_pista = {}  # pista -> instante en que queda libre
	tags = []
	for i, c in enumerate(sorted(cues, key=lambda c: c[1])):
		name, t = c[0], c[1]
		vol = c[2] if len(c) > 2 else VOL.get(name, 0.35)
		f = src / f"{name}.mp3"
		if name not in medidas:
			medidas[name] = medir(f)
		pico, dur = medidas[name]
		shutil.copy(f, p / "assets" / "sfx" / f"{name}.mp3")
		start = max(0.0, t - pico + FRAME)
		pista = next(k for k in range(4, 40) if fin_pista.get(k, 0) <= start)
		fin_pista[pista] = start + dur
		tags.append(f'\t\t<audio id="sfx{i}" class="clip" src="assets/sfx/{name}.mp3" data-start="{start:.3f}" '
			f'data-duration="{dur}" data-track-index="{pista}" data-volume="{vol}"></audio>')
	idx = p / "index.html"
	s = idx.read_text(encoding="utf-8")
	s = re.sub(r'\n\s*<audio id="sfx\d+"[^\n]*</audio>', "", s)
	ancla = re.search(r'\n(\s*)<audio id="voz"[^\n]*</audio>', s)
	s = s[: ancla.end()] + "\n" + "\n".join(tags) + s[ancla.end():]
	idx.write_text(s, encoding="utf-8")
	print(f"{len(tags)} efectos en {proyecto}")


if __name__ == "__main__":
	main(*sys.argv[1:4])
