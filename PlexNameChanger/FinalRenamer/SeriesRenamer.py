import os
import re
import csv
import json
import pickle
import urllib.request
import urllib.parse
import sys
import re

# ========== RUTAS ==========
def obtener_ruta_archivo(rel_path):
    base_path = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
    return os.path.join(base_path, rel_path)

# ========== EXTRACCIÓN DE DATOS OFFLINE (IMDb) ==========
def cargar_title_basics():
    path = obtener_ruta_archivo('imdb_data/title.basics.tsv')
    cache = obtener_ruta_archivo('imdb_data/title_basics.pkl')
    if os.path.exists(cache):
        with open(cache, 'rb') as f:
            return pickle.load(f)

    titulos = {}
    with open(path, encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            if row['titleType'] in ('tvEpisode', 'tvSeries', 'tvMiniSeries', 'tvSpecial'):
                titulos[row['tconst']] = row['primaryTitle']

    with open(cache, 'wb') as f:
        pickle.dump(titulos, f)
    return titulos

def cargar_title_episodes():
    path = obtener_ruta_archivo('imdb_data/title.episode.tsv')
    cache = obtener_ruta_archivo('imdb_data/title_episode.pkl')
    if os.path.exists(cache):
        with open(cache, 'rb') as f:
            return pickle.load(f)

    episodios = []
    with open(path, encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            if row['seasonNumber'] != '\\N' and row['episodeNumber'] != '\\N':
                episodios.append({
                    'tconst': row['tconst'],
                    'parentTconst': row['parentTconst'],
                    'season': int(row['seasonNumber']),
                    'episode': int(row['episodeNumber'])
                })

    with open(cache, 'wb') as f:
        pickle.dump(episodios, f)
    return episodios

def construir_estructura_imdb(titulos, episodios):
    estructura = {}
    for ep in episodios:
        serie_id = ep['parentTconst']
        cod = f"S{ep['season']:02}E{ep['episode']:02}"
        nombre_serie = titulos.get(serie_id, None)
        if not nombre_serie:
            continue
        titulo_episodio = titulos.get(ep['tconst'], "Título Desconocido")
        estructura.setdefault(nombre_serie, {})[cod] = titulo_episodio
    return estructura

# ========== CARGA DE DATOS CACHEADOS DE TVMAZE ==========
def cargar_cache_tvmaze():
    cache_dir = obtener_ruta_archivo('tvmaze_cache')
    estructura = {}
    if not os.path.exists(cache_dir):
        return estructura

    for archivo in os.listdir(cache_dir):
        if archivo.endswith('.pkl'):
            nombre_serie = archivo[:-4].replace('_', ' ').title()
            with open(os.path.join(cache_dir, archivo), 'rb') as f:
                episodios = pickle.load(f)
                estructura[nombre_serie] = {}
                for ep in episodios:
                    cod = f"S{ep['season']:02}E{ep['number']:02}"
                    estructura[nombre_serie][cod] = ep['name']
    return estructura

# ========== FUNCIONES ONLINE: API TVMAZE ==========
def obtener_serie_tvmaze(nombre_serie):
    try:
        nombre_codificado = urllib.parse.quote(nombre_serie)
        url = f"https://api.tvmaze.com/singlesearch/shows?q={nombre_codificado}"
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read()) if response.status == 200 else None
    except Exception as e:
        print(f"❌ Error al buscar serie en TVMaze: {e}")
    return None

def obtener_episodios_tvmaze(serie_id):
    try:
        url = f"https://api.tvmaze.com/shows/{serie_id}/episodes"
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read()) if response.status == 200 else []
    except Exception as e:
        print(f"❌ Error al obtener episodios de TVMaze: {e}")
    return []

def buscar_episodios_online(nombre_serie):
    serie_data = obtener_serie_tvmaze(nombre_serie)
    if not serie_data:
        print("❌ Serie no encontrada en TVMaze.")
        return None
    episodios = obtener_episodios_tvmaze(serie_data['id'])

    cache_dir = obtener_ruta_archivo('tvmaze_cache')
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"{nombre_serie.lower().replace(' ', '_')}.pkl")
    with open(cache_path, 'wb') as f:
        pickle.dump(episodios, f)
    print(f"💾 Guardado en caché: {cache_path}")
    return episodios

# ========== UTILIDADES ==========
def obtener_directorio_series():
    base_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
    return os.path.normpath(os.path.abspath(os.path.join(base_dir, "..")))

def palabras_clave(titulo):
    return((re.sub(r'[^a-z0-9 ]', '', titulo.lower())).strip().split())
def extraer_se_temp(nombre_archivo):
    patrones = [
        r'season[^\d]*(\d+)[^\d]*episode[^\d]*(\d+)',  # season X episode X
        r's(\d{1,2})e(\d{1,2})',                       # s01e01
        r's(\d{1,2})[^\w]?e(\d{1,2})',                 # s1e1
        r'(\d{1,2})x(\d{1,2})',                       # 1x01
        r'(\d{1,2})\s*-\s*(\d{1,2})'
    ]
    nombre_archivo = nombre_archivo.lower().replace("_", " ").replace(".", " ")
    for patron in patrones:
        match = re.search(patron, nombre_archivo)
        if match:
            return match.group(1).zfill(2), match.group(2).zfill(2)
    return None, None

def buscar_series_por_nombre(nombre, estructura):
    nombre_norm = palabras_clave(nombre)
    coincidencias = []
    for clave in estructura:
        palabras_serie = palabras_clave(clave)
        coincidencia = len(set(nombre_norm) & set(palabras_serie))
        if coincidencia > 0:
            coincidencias.append((clave, coincidencia))

    coincidencias.sort(key=lambda x: x[1], reverse=True)
    return [clave for clave, _ in coincidencias]

def limpiar_nombre(nombre):
    return re.sub(r'[\\/:"*?<>|]+', '', nombre)

# ========== RENOMBRADO DE ARCHIVOS ==========
def renombrar_archivos(carpeta, clave_estructura, nombre_serie, estructura, episodios_online=None):
    ruta_carpeta = os.path.join(os.path.dirname(os.path.dirname(obtener_ruta_archivo(""))), carpeta)
    archivos = [f for f in os.listdir(ruta_carpeta) if f.endswith(('.mp4', '.mkv'))]

    for archivo in archivos:
        temporada, episodio = extraer_se_temp(archivo)
        if not temporada or not episodio:
            print(f"❌ No se pudo extraer info de: {archivo}")
            continue
        cod = f"S{temporada}E{episodio}"

        if episodios_online:
            titulo = next((ep['name'] for ep in episodios_online if ep['season'] == int(temporada) and ep['number'] == int(episodio)), None)
        else:
            titulo = estructura.get(clave_estructura, {}).get(cod)

        if not titulo:
            print(f"⚠️ No encontrado: {cod}")
            continue

        ext = os.path.splitext(archivo)[1]
        nuevo_nombre = f"{nombre_serie} - {cod} - {limpiar_nombre(titulo)}{ext}"
        try:
            os.rename(os.path.join(ruta_carpeta, archivo), os.path.join(ruta_carpeta, nuevo_nombre))
            print(f"✅ {archivo} → {nuevo_nombre}")
        except Exception as e:
            print(f"❌ Error al renombrar {archivo}: {e}")

# ========== MENÚ PRINCIPAL ==========

def menu():
    print("📁 Carpetas detectadas:")
    renamer_dir = os.path.normpath(os.path.abspath(obtener_ruta_archivo("")))
    print("La ruta es: " + renamer_dir)
    # Corrección: subimos dos niveles si estamos dentro del .exe (modo frozen)
    raiz = obtener_directorio_series()

    carpetas = [f for f in os.listdir(raiz) if (os.path.isdir(os.path.join(raiz, f)) and os.path.join(raiz, f) != renamer_dir)]

    for i, carpeta in enumerate(carpetas):
        print(f"{i+1}. {carpeta}")

    seleccion = int(input("Selecciona una serie por número (0 para salir): "))
    if seleccion == 0:
        return
    carpeta_serie = carpetas[seleccion - 1]

    # Primero, buscamos en cache de TVMaze
    print("🔍 Buscando en cache de TVMaze...")
    estructura_tvmaze = cargar_cache_tvmaze()
    posibles_tvmaze = buscar_series_por_nombre(carpeta_serie, estructura_tvmaze)

    if posibles_tvmaze:
        print("✅ Encontradas las siguientes coincidencias:")
        for i, serie in enumerate(posibles_tvmaze):
            print(f"{i+1}. {serie}")
        seleccion = int(input("Elige desde dónde renombrar (0 para abortar): "))
        while seleccion != 0 and seleccion not in range(1, len(posibles_tvmaze) + 1):
            print("Debe introducir un número válido")
            seleccion = int(input("Elige desde dónde renombrar (0 para abortar): "))

        if seleccion > 0:
            nombre_serie = posibles_tvmaze[seleccion - 1]
            clave = nombre_serie
            renombrar_archivos(carpeta_serie, clave, nombre_serie, estructura_tvmaze)
            return

    print("🔍 No encontrada en cache de TVMaze. Buscando en IMDb...")
    titulos = cargar_title_basics()
    episodios = cargar_title_episodes()
    estructura_imdb = construir_estructura_imdb(titulos, episodios)
    posibles_imdb = buscar_series_por_nombre(carpeta_serie, estructura_imdb)

    if posibles_imdb:
        print("✅ Encontradas las siguientes coincidencias:")
        for i, nombre in enumerate(posibles_imdb, 1):
            print(f"{i}. {nombre}")
        seleccion = int(input("Elige desde dónde renombrar (0 para abortar): "))
        if seleccion == 0:
            return
        nombre_serie = posibles_imdb[seleccion - 1]
        clave = nombre_serie
        renombrar_archivos(carpeta_serie, clave, nombre_serie, estructura_imdb)
        return

    print("❓ Serie no encontrada en ninguna fuente local.")
    if input("🌐 ¿Buscar online en TVMaze? [y/n]: ") == 'y':
        episodios_online = buscar_episodios_online(carpeta_serie)
        if episodios_online:
            renombrar_archivos(carpeta_serie, None, carpeta_serie, {}, episodios_online)
        else:
            print("❌ Serie no encontrada online.")
    else:
        print("⏹️ Operación cancelada.")

# ========== EJECUCIÓN ==========
if __name__ == "__main__":
    menu()

