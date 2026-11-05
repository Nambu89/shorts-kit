---
name: shorts-kit
description: Hacer un Short técnico vertical (50-60 s) con voz clonada, animación en HyperFrames, subtítulos palabra a palabra, guía en PDF y paquete de publicación para YouTube y LinkedIn. Úsala cuando pidan un vídeo o píldora sobre Fabric, Power BI u otro tema de Microsoft.
---

# Shorts técnicos con IA

Un Short es: guion de unos 140-160 palabras → voz → escenas animadas que van al ritmo de la voz → subtítulos → efectos → render → guía en PDF y textos para publicar.
Los scripts están en `scripts/` de este repo. Todos los comandos se ejecutan desde la raíz del kit.

## 0. Antes de empezar
- Node 20+, Python 3.11+, ffmpeg y `pip install -r requirements.txt`.
- Modelo de transcripción: descarga `sherpa-onnx-whisper-small` de las releases de sherpa-onnx (GitHub, etiqueta `asr-models`) y descomprímelo en `models/`, o apunta `WHISPER_DIR` a donde lo tengas.
- Efectos de sonido: mp3 cortos en `sfx/` (pop, whoosh, click-soft…). Usa solo efectos cuya licencia permita usarlos en tus vídeos.
- Iconos de producto: descárgalos tú de las páginas oficiales (ver README). Mira las condiciones de uso: sin recortar, girar ni deformar, y con el nombre del producto cerca.

## 1. Investigar
- Todo dato del vídeo y de la guía sale de Microsoft Learn (el conector de Microsoft Learn si lo tienes). Guarda las URL: van en la guía y en la descripción.
- Comprueba qué está en preview y qué es GA, y las regiones si las mencionas. Si algo no está claro en la documentación, no lo digas.

## 2. Guion (`templates/guion.md`)
- Estructura: gancho con una pregunta (0-7 s) → opción 1 → opción 2 → cuándo usar cada una → regla final → «guía gratis en <web>/guias».
- Frases cortas. Una idea por frase: cada frase será un tramo y una escena o un cambio en pantalla.
- Escríbelo para que se pronuncie bien:
	- Siglas que se leen como palabra, en minúscula: «api», no «API» (si no, la voz lo deletrea).
	- Números como quieres que suenen: «tres seis cinco».
	- Prueba los nombres de producto raros con una frase corta antes de generar todo.
- Enséñale el guion al usuario y espera su OK antes de generar la voz.

## 3. Voz
- ElevenLabs con la voz clonada del usuario. Si el conector no permite descargar el audio, pide al usuario que lo descargue y lo adjunte.
- Guarda el audio como `<proyecto>/assets/voz.wav`.
- Si algo suena mal, regenera solo esa toma con el texto corregido. No intentes arreglarlo en el montaje.

## 4. Proyecto y tramos
```
python scripts/nuevo_proyecto.py ../short-<tema>
python scripts/trocear.py ../short-<tema>/assets/voz.wav ../short-<tema>/tramos.json
```
- `tramos.json` da cada frase con su inicio y fin. Si dos frases salen juntas, repite con `--fino`.
- Escribe `textos.json`: la lista de textos de cada tramo, tal como deben verse en los subtítulos (con la ortografía correcta, no la de Whisper).
- Las escenas empiezan y acaban en los límites de los tramos.

## 5. Escenas
- Copia `examples/demo/escenas.py` y escribe una función por escena con las piezas de `scripts/scenes_lib.py` (heading, tool, chip, svg_lines, travel, typewrite…).
- Cada cosa aparece cuando la voz la nombra: mira el tiempo en `tramos.json` (y en `assets/words.json` tras el paso 6) y resta el inicio de la escena.
- Reglas que ya nos han costado un render:
	- Ids únicos en todo el Short.
	- No animar `x` sobre un elemento con `transform` en su CSS. `chip()` ya centra sin transform.
	- Algo visible en el segundo 0 (es la portada por defecto).
	- Textos de 28 px como mínimo.
	- Si el check dice `text_box_overflow`, acorta el texto o baja `size`.

## 6. Subtítulos y efectos
```
python scripts/captions_build.py tramos.json textos.json ../short-<tema> "#FFB347" <duración>
python scripts/sfx_build.py ../short-<tema> cues.json sfx
```
- `cues.json`: `[["pop", 3.0], ["whoosh", 6.9, 0.3], ...]` con el tiempo absoluto en que aparece la imagen. El script cuadra el golpe del efecto con ella.
- Pocos efectos: un pop cuando aparece algo importante y un whoosh en los cambios de escena.
- Si una sigla tiene los subtítulos desfasados, añádela a `PESO` en `captions_build.py`.

## 7. Revisar y renderizar
```
cd ../short-<tema>
npm run check
npx --yes hyperframes@0.8.191 snapshot --at 2,10,25,40 --no-end -o snaps
npm run render -- -o renders/raw.mp4
ffmpeg -i renders/raw.mp4 -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 -c:a aac -b:a 192k renders/short-<tema>.mp4
```
- `check` tiene que pasar sin errores.
- Mira los fotogramas: nada cortado, nada solapado con los subtítulos (franja de 1235 px hacia abajo), el texto se lee en un móvil.
- La normalización deja el volumen a −14 LUFS, el nivel de YouTube.

## 8. Guía en PDF
```
python scripts/guide_pdf/gen_guide.py contenido.py guia-<tema>.pdf ../short-<tema>/assets/fonts
```
- Copia `scripts/guide_pdf/ejemplo_contenido.py`. Unas 8 páginas: portada, opciones, comparativa, casos, trampas y una chuleta final.
- Cada dato con su fuente. Revisa el HTML que deja al lado del PDF si algo se sale.
- La última escena del vídeo enseña la portada de **esta** guía y la URL de la página de guías (siempre la misma URL).

## 9. Paquete de publicación (`templates/paquete.md`)
- YouTube: título de menos de 60 caracteres con la palabra que se busca, descripción con fuentes y enlace a la guía, etiquetas y comentario fijado.
- LinkedIn: sube el mp4 nativo (no el enlace de YouTube) y pon el enlace a la guía en el primer comentario.
- Propón días y horas, pero que publique el usuario: no automatices sus redes.
