# Estructura base del proyecto HomeTV con exploración automática de series

# --- canal.py ---
import random
from datetime import datetime

class Canal:
    def __init__(self, nombre, series, hora_cambio=None):
        self.nombre = nombre
        self.series = series
        self.capitulo_actual = random.choice(series)
        self.hora_cambio = hora_cambio or datetime.now()
        self.t_inicio = random.randint(0, self.capitulo_actual['duracion'])  # en segundos

    def obtener_progreso_actual(self):
        ahora = datetime.now()
        delta = (ahora - self.hora_cambio).total_seconds()
        return min(self.t_inicio + delta, self.capitulo_actual['duracion'])

    def cambiar_a(self, nuevo_capitulo):
        self.capitulo_actual = nuevo_capitulo
        self.t_inicio = 0
        self.hora_cambio = datetime.now()

    def serializar_para_html(self):
        return {
            "ruta": self.capitulo_actual["ruta"],
            "progreso_inicio": self.obtener_progreso_actual()
        }

# --- control.py ---
import json
import webbrowser
from pathlib import Path
from canal import Canal
import os
import re

DATA_DIR = Path("data")
PLAYER_PATH = Path("player/index.html")
SERIES_DIR = Path("/mnt/backups/series")

# Función para escanear automáticamente episodios en la estructura
# /mnt/backups/series/nombreSerie/seasonAA/nombreSerie - sAAeBB - nombreEpisodio.mp4

def obtener_series():
    episodios = []
    for serie_dir in SERIES_DIR.iterdir():
        if not serie_dir.is_dir():
            continue
        for season_dir in serie_dir.glob("season*"):
            for archivo in season_dir.glob("*.mp4"):
                match = re.search(r's(\d+)e(\d+)', archivo.name, re.IGNORECASE)
                if match:
                    duracion_ficticia = 1200 + random.randint(-300, 300)  # entre 15 y 25 min
                    episodios.append({
                        "ruta": str(archivo.relative_to(SERIES_DIR.parent)),
                        "duracion": duracion_ficticia
                    })
    return episodios

series_detectadas = obtener_series()
canal_actual = Canal("Canal Aleatorio", series_detectadas)

def guardar_estado():
    estado = canal_actual.serializar_para_html()
    with open(DATA_DIR / "current_video.json", "w", encoding="utf-8") as f:
        json.dump(estado, f, indent=2)

def reproducir():
    guardar_estado()
    webbrowser.open(PLAYER_PATH.absolute().as_uri())

if __name__ == "__main__":
    reproducir()

# --- player/index.html ---
# (Crea este archivo en player/index.html)
'''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>HomeTV</title>
</head>
<body>
  <h1>Reproductor HomeTV</h1>
  <video id="player" controls autoplay width="800"></video>

  <script>
    fetch("../data/current_video.json")
      .then(res => res.json())
      .then(data => {
        const video = document.getElementById("player");
        video.src = "../" + data.ruta;
        video.currentTime = data.progreso_inicio;
        video.play();
      });
  </script>
</body>
</html>
'''

# --- Estructura de carpetas sugerida ---
# homeTV/
# ├── canal.py
# ├── control.py
# ├── data/
# │   └── current_video.json (se genera)
# ├── player/
# │   └── index.html
# └── /mnt/backups/series/
#     ├── The Office/
#     │   └── season01/
#     │       └── The Office - s01e01 - Pilot.mp4
#     └── Breaking Bad/
#         └── season02/
#             └── Breaking Bad - s02e01 - Seven Thirty-Seven.mp4
