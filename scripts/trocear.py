"""Corta un audio por silencios y transcribe cada trozo con Whisper small (sherpa-onnx).

Uso: python trocear.py audio.wav salida.json [--fino]
Salida: lista de {start, end, text} con tiempos en segundos del audio original.

El modelo se busca en la carpeta de la variable WHISPER_DIR (por defecto ./models/sherpa-onnx-whisper-small).
--fino corta con silencios más cortos (0,18 s): útil si un tramo junta dos frases.
"""
import json
import os
import re
import subprocess
import sys

import numpy as np
import sherpa_onnx
import soundfile as sf

M = os.environ.get("WHISPER_DIR", "models/sherpa-onnx-whisper-small")


def silencios(path, d=0.35):
	"""Devuelve [(inicio, fin)] de silencios según ffmpeg silencedetect."""
	err = subprocess.run(
		["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=noise=-38dB:d={d}", "-f", "null", "-"],
		capture_output=True, text=True,
	).stderr
	ini = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", err)]
	fin = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", err)]
	return list(zip(ini, fin))


def main(path, out, fino=False):
	audio, sr = sf.read(path, dtype="float32")
	if audio.ndim > 1:
		audio = audio.mean(axis=1)
	dur = len(audio) / sr
	sil = silencios(path, 0.18 if fino else 0.35)
	# Trozos de voz = huecos entre silencios
	tramos, t = [], 0.0
	for s, e in sil:
		if s - t > 0.15:
			tramos.append((t, s))
		t = e
	if dur - t > 0.15:
		tramos.append((t, dur))

	rec = sherpa_onnx.OfflineRecognizer.from_whisper(
		encoder=f"{M}/small-encoder.int8.onnx",
		decoder=f"{M}/small-decoder.int8.onnx",
		tokens=f"{M}/small-tokens.txt",
		language="es",
		task="transcribe",
		num_threads=4,
	)
	res = []
	for a, b in tramos:
		# Margen de 0,1 s para no comer el ataque de la primera sílaba
		i0, i1 = max(0, int((a - 0.1) * sr)), min(len(audio), int((b + 0.1) * sr))
		trozo = audio[i0:i1]
		if sr != 16000:
			n = int(len(trozo) * 16000 / sr)
			trozo = np.interp(np.linspace(0, len(trozo) - 1, n), np.arange(len(trozo)), trozo).astype("float32")
		st = rec.create_stream()
		st.accept_waveform(16000, trozo)
		rec.decode_stream(st)
		txt = st.result.text.strip()
		res.append({"start": round(a, 3), "end": round(b, 3), "text": txt})
		print(f"{a:6.2f}–{b:6.2f}  {txt}")
	json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
	main(sys.argv[1], sys.argv[2], "--fino" in sys.argv[3:])
