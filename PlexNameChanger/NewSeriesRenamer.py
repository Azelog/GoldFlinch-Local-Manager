import os
import re
import csv
import urllib.request
import json

# ========== CARGA DE DATOS IMDb OFFLINE ==========

def cargar_title_basics(path='imdb_data/title.basics.tsv'):
    titulos = {}
    with open(path, encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            if row['titleType'] == 'tvEpisode':
                titulos[row['tconst']] = row['primaryTitle']
    return titulos

def cargar_title_episodes(path='imdb_data/title.episode.tsv'):
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
    return episodios

def construir_estructura_series(titulos, episodios):
    estructura = {}
    for ep in episodios:
        serie_id = ep['parentTconst']
        cod = f"S{ep['season']:02}E{ep['episode']:02}"
        titulo = titulos.get(ep['tconst'], "Título Desconocido")
        if serie_id not in estructura:
            estructura[serie_id] = {}
        estructura[serie_id][cod] = titulo
    return estructura

def buscar_series_por_nombre(nombre, estructura, titulos):
    nombre = nombre.lower()
    coincidencias = []
    for parent_id in estructura.keys():
        nombre_serie = titulos.get(parent_id, "")
        if nombre in nombre_serie.lower():
            coincidencias.append((parent_id, nombre_serie))
    return coincidencias

# ========== FUNCIONALIDAD ONLINE: TVMaze API (USANDO urllib) ==========

def obtener_serie_tvmaze(nombre_serie):
    """Obtiene la serie desde TVMaze usando su API con urllib"""
    url = f"https://api.tvmaze.com/singlesearch/shows?q={nombre_serie}"
    with urllib.request.urlopen(url) as response:
        if response.status == 200:
            return json.loads(response.read())
        else:
            return None

def obtener_episodios_tvmaze(serie_id):
    """Obtiene los episodios de una serie desde TVMaze con urllib"""
    url = f"https://api.tvmaze.com/shows/{serie_id}/episodes"
    with urllib.request.urlopen(url) as response:
        if response.status == 200:
            return json.loads(response.read())
        else:
            return []

def buscar_episodios_online(nombre_serie):
    """Busca los episodios online usando TVMaze con urllib"""
    serie_data = obtener_serie_tvmaze(nombre_serie)
    if not serie_data:
        print(f"❌ No se encontró la serie {nombre_serie} en TVMaze.")
        return None

    serie_id = serie_data['id']
    episodios = obtener_episodios_tvmaze(serie_id)
    return episodios

# ========== UTILIDADES ==========

def extraer_se_temp(nombre_archivo):
    patrones = [
        r'season[^\d]*(\d+)[^\d]*episode[^\d]*(\d+)',
        r's(\d{1,2})e(\d{1,2})',
        r's(\d{1,2})[^\w]?e(\d{1,2})'
    ]
    nombre_archivo = nombre_archivo.lower().replace("_", " ").replace(".", " ")
    for patron in patrones:
        match = re.search(patron, nombre_archivo)
        if match:
            return match.group(1).zfill(2), match.group(2).zfill(2)
    return None, None

def prepareSubstitution(pathOrigin,newName):
    line = f"{pathOrigin} => newName\n"
    open("prepared_substitution.txt","w").write(line)

def renombrar_archivos(carpeta, serie_id, nombre_serie, estructura, episodios_online=None):
    carpetas = [f for f in os.listdir(carpeta) if os.isdir(carpeta)]
    for i in carpetas:
        if os.isdir(i):
            data = i.split(" - ")
            season = data[1]
            for j in os.walk(f'{pathSeries}/{i}'):
                if f.endswith(('.mp4', '.mkv')):
                    prepareSubstitution(f'{pathSeries}/{i}/j',f'{season} j')
        else:
            episodeCode = detectEpisodeCode(i)
            prepareSubstitution(f'{pathSeries}/i',createEpisodeName(SeriesID,episodeCode))
    archivos = [f for f in os.listdir(carpeta) if f.endswith(('.mp4', '.mkv'))]
    for archivo in archivos:
        temporada, episodio = extraer_se_temp(archivo)
        if not temporada or not episodio:
            print(f"❌ No se pudo extraer info de: {archivo}")
            continue
        cod = f"S{temporada}E{episodio}"

        # Si no hay episodios online, usa la estructura offline (IMDb .tsv)
        if episodios_online:
            titulo = next((ep['name'] for ep in episodios_online if ep['season'] == int(temporada) and ep['number'] == int(episodio)), None)
        else:
            titulo = estructura[serie_id].get(cod)

        if not titulo:
            print(f"⚠️ No encontrado en datos: {cod}")
            continue

        ext = os.path.splitext(archivo)[1]
        nuevo_nombre = f"{nombre_serie} - {cod} - {titulo}{ext}"
        try:
            os.rename(os.path.join(carpeta, archivo), os.path.join(carpeta, nuevo_nombre))
            print(f"✅ {archivo} → {nuevo_nombre}")
        except Exception as e:
            print(f"❌ Error al renombrar {archivo}: {e}")

# ========== MENÚ PRINCIPAL ==========

def menu():
    print("📁 Carpetas detectadas:")
    carpetas = [f for f in os.listdir() if os.path.isdir(f)]
    for i, carpeta in enumerate(carpetas):
        print(f"{i+1}. {carpeta}")
    seleccion = int(input("Selecciona una serie por número (0 para salir): "))
    if seleccion == 0:
        return
    carpeta_serie = carpetas[seleccion - 1]

    print("🔄 Cargando datos de IMDb...")
    titulos = cargar_title_basics()
    episodios = cargar_title_episodes()
    estructura = construir_estructura_series(titulos, episodios)

    posibles_series = buscar_series_por_nombre(carpeta_serie, estructura, titulos)
    if not posibles_series:
        print("❌ No se encontró ninguna serie con ese nombre.")
        print("¿Quieres intentar buscar en TVMaze online?")
        opcion_online = input("1. Sí  2. No: ")
        if opcion_online == '1':
            episodios_online = buscar_episodios_online(carpeta_serie)
            if episodios_online:
                renombrar_archivos(carpeta_serie, None, carpeta_serie, estructura, episodios_online)
        return

    print("🎯 Series coincidentes:")
    for i, (_, nombre) in enumerate(posibles_series):
        print(f"{i+1}. {nombre}")

    # Añadimos la opción de buscar online en TVMaze como la última opción
    print(f"{len(posibles_series) + 1}. Buscar online en TVMaze")

    eleccion = int(input("Elige la serie (0 para cancelar): "))
    if eleccion == 0:
        return

    if eleccion == len(posibles_series) + 1:
        # Buscar en TVMaze
        episodios_online = buscar_episodios_online(carpeta_serie)
        if episodios_online:
            renombrar_archivos(carpeta_serie, None, carpeta_serie, estructura, episodios_online)
        return

    serie_id, nombre_serie = posibles_series[eleccion - 1]

    opcion_online = input("¿Quieres intentar buscar episodios online con TVMaze? (1. Sí, 2. No): ")
    episodios_online = None
    if opcion_online == '1':
        episodios_online = buscar_episodios_online(nombre_serie)

    renombrar_archivos(carpeta_serie, serie_id, nombre_serie, estructura, episodios_online)

# ========== EJECUCIÓN ==========
if __name__ == "__main__":
    menu()

