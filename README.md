# shorts-kit

Kit para hacer Shorts técnicos verticales (50-60 s) con IA: guion, voz clonada, animación con [HyperFrames](https://hyperframes.heygen.com), subtítulos palabra a palabra, guía en PDF y textos para YouTube y LinkedIn.

Es el método con el que hago los Shorts de [@Nambu89](https://www.youtube.com/@Nambu89). Funciona con cualquier tema; el ejemplo es de Power BI.

## Cómo se usa
La forma más cómoda es con Claude Code: abre esta carpeta y pide «hazme un Short sobre <tema>». La skill `.claude/skills/shorts-kit/SKILL.md` le explica el proceso paso a paso, con las reglas que hemos aprendido a base de renders fallidos.

También puedes seguir los pasos de la skill a mano.

## Instalación
1. Node 20 o superior, Python 3.11 o superior y ffmpeg.
2. `pip install -r requirements.txt` y después `playwright install chromium` (para la guía en PDF).
3. Modelo de transcripción (unos 600 MB): descarga [sherpa-onnx-whisper-small.tar.bz2](https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2) y descomprímelo en `models/`.
4. Efectos de sonido: mp3 cortos en `sfx/` con el nombre que uses en `cues.json` (`pop.mp3`, `whoosh.mp3`, `click-soft.mp3`…). No vienen en el kit por su licencia: usa los tuyos.
5. Voz: tu propia cuenta de ElevenLabs con tu voz clonada.

## Prueba rápida (2 minutos)
```
python scripts/nuevo_proyecto.py ../short-demo
# pon un audio cualquiera de unos 12 s en ../short-demo/assets/voz.wav
python examples/demo/escenas.py ../short-demo
python scripts/captions_build.py examples/demo/tramos.json examples/demo/textos.json ../short-demo "#FFB347" 12
python scripts/sfx_build.py ../short-demo examples/demo/cues.json sfx
cd ../short-demo
npm run check
npm run render -- -o renders/demo.mp4
```

## Qué hay
| Archivo | Para qué |
|---|---|
| `scripts/nuevo_proyecto.py` | Crea la carpeta de un Short: HyperFrames, GSAP, fuentes e iconos |
| `scripts/trocear.py` | Corta la voz por silencios y la transcribe: inicio y fin de cada frase |
| `scripts/scenes_lib.py` | Piezas y animaciones para las escenas (títulos, iconos, etiquetas, líneas, datos que viajan, texto que se escribe) |
| `scripts/captions_build.py` | Subtítulos palabra a palabra sincronizados con la voz |
| `scripts/sfx_build.py` | Coloca los efectos de sonido para que el golpe caiga con la imagen |
| `scripts/guide_pdf/gen_guide.py` | Guía en PDF de 1080×1350 (vale también como carrusel de LinkedIn) |
| `templates/` | Plantillas del guion y del paquete de publicación |
| `examples/demo/` | Short de ejemplo de 12 s |
| `assets/icons/` | Iconos genéricos propios (bot, datos, gráfico, tabla) |

## Iconos de producto
No vienen en el kit. Descárgalos de las páginas oficiales y respeta sus condiciones (sin recortar, girar ni deformar, con el nombre del producto al lado):
- [Microsoft Fabric](https://learn.microsoft.com/fabric/fundamentals/icons)
- [Power Platform (incluye Power BI)](https://learn.microsoft.com/power-platform/guidance/icons)
- [Azure](https://learn.microsoft.com/azure/architecture/icons)

Copia los SVG que uses a `<proyecto>/assets/icons/` y llámalos por su nombre en `tool()`.

## Notas
- HyperFrames va fijado a la versión 0.8.191, que es la que está probada. Si actualizas, vuelve a pasar `npm run check` al ejemplo.
- Los textos de la guía y del vídeo tienen que salir de la documentación oficial, con su fuente.
