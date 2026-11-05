"""Contenido de ejemplo para gen_guide.py. Copia este archivo y cambia los textos.

Todo lo que pongas aquí tiene que salir de la documentación oficial (Microsoft Learn): cita la fuente.
"""
TITULO = "¿Import o DirectQuery?"
SUBTITULO = "Cuándo copiar los datos al modelo y cuándo consultarlos en el origen. (Texto de ejemplo: compruébalo en Microsoft Learn antes de publicar.)"
AUTOR = "Tu nombre · Tu rol"
WEB = "tuweb.dev"
FUENTE = "Microsoft Learn"
FECHA = "nov. 2026"

PAGINAS = [
	("LAS DOS OPCIONES", "Copiar o consultar", [
		("card", "Import", "Los datos se copian al modelo. Texto de ejemplo."),
		("card", "DirectQuery", "Las consultas van al origen. Texto de ejemplo."),
	]),
	("EN RESUMEN", "Qué mirar", [
		("row", "Volumen", "Texto de ejemplo."),
		("row", "Frescura", "Texto de ejemplo."),
		("row", "Rendimiento", "Texto de ejemplo."),
		("p", f"Más guías gratis en {WEB} · {FECHA}"),
	]),
]
