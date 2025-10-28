import pandas as pd
import requests
import re
import pickle
from pathlib import Path

# --- CONFIGURACIÓN ---
IMDB_DIR = Path("/IMDBdatabase/")  # contiene title.basics.tsv, title.episode.tsv, etc.
PKL_DIR = Path("/ListaDeseados")
PKL_DIR.mkdir(exist_ok=True)

# --- 1️⃣ Buscar series en TVMaze ---
def buscar_series_tvmaze(nombre):
    url = f"https://api.tvmaze.com/search/shows?q={nombre}"
    resp = requests.get(url)
    if resp.status_code != 200:
        print("❌ Error: fallo al buscar en tvmaze resp.status_code != 200")
        return []

    resultados = []
    for entry in resp.json():
        show = entry["show"]
        nombre_show = show.get("name", "Desconocido")
        imdb_id = show.get("externals", {}).get("imdb", "")
        if not imdb_id:
            imdb_id = ""
        codigo = {nombre_show:imdb_id}
        resultados.append(codigo)

    return resultados

# --- 2️⃣ Indexar serie en IMDb local ---
def indexar_serie_local(nombre):
    basics = pd.read_csv(IMDB_DIR / "title.basics.tsv", sep="\t", dtype=str, low_memory=False)
    episodes = pd.read_csv(IMDB_DIR / "title.episode.tsv", sep="\t", dtype=str, low_memory=False)

    # Filtrar series
    series = basics[basics["titleType"] == "tvSeries"]
    serie_row = series[series["primaryTitle"].str.contains(nombre, case=False, na=False)]

    if serie_row.empty:
        print("❌ Serie no encontrada en IMDb local")
        return None

    serie_id = serie_row.iloc[0]["tconst"]

    eps = episodes[episodes["parentTconst"] == serie_id]
    resultados = []
    for _, ep in eps.iterrows():
        ep_id = ep["tconst"]
        temporada = ep.get("seasonNumber", "0") or "0"
        episodio = ep.get("episodeNumber", "0") or "0"

        # Buscar título del episodio
        ep_title = basics.loc[basics["tconst"] == ep_id, "primaryTitle"].values
        ep_title = ep_title[0] if len(ep_title) else "Sin título"

        # Crear el nombre con el formato personalizado
        nombre_formateado = (
            f"{nombre_serie} - S{int(temporada):02d}E{int(episodio):02d} - "
            f"{ep_title} - SDQ - {ep_id} - Series"
        )
        resultados.append(nombre_formateado)

    salida = PKL_DIR / f"{nombre}.pkl"
    with open(salida, "wb") as f:
        pickle.dump(resultados, f)
    print(f"✅ Guardado {len(resultados)} episodios en {salida}")

    return salida

# --- 3️⃣ Buscar películas ---
def buscar_peliculas(nombre):
    basics = pd.read_csv(IMDB_DIR / "title.basics.tsv", sep="\t", dtype=str, low_memory=False)
    peliculas = basics[basics["titleType"] == "movie"]
    coincidencias = peliculas[peliculas["primaryTitle"].str.contains(nombre, case=False, na=False)]

    resultados = []
    for _, row in coincidencias.iterrows():
        nombre_peli = row["primaryTitle"]
        imdb_id = row["tconst"]
        codigo = f"{nombre_peli} - S0E0 - {nombre_peli} - SDQ - {imdb_id} - Movies"
        resultados.append(codigo)
    return resultados


# --- 4️⃣ Indexar película local ---
def indexar_pelicula_local(nombre):
    salida = PKL_DIR / f"{Movies}.pkl"
     # Cargar datos previos si existen
    if os.path.exists(salida):
        with open(salida, "rb") as f:
            try:
                data = pickle.load(f)
            except EOFError:
                data = {}
    else:
        data = {}

    # Actualizar
    data.update(nombre)

    # Guardar nuevamente
    with open(salida, "wb") as f:
        pickle.dump(data, f)
    return salida


# --- 🔍 Ejemplo de uso ---
if __name__ == "__main__":
    print("=== Búsqueda de series ===")
    for s in buscar_series_tvmaze("Iron Man"):
        print(s)

    print("\n=== Búsqueda de películas ===")
    for p in buscar_peliculas("Iron Man"):
        print(p)

    print("\n=== Indexando serie ===")
    indexar_serie_local("Iron Man")

    print("\n=== Indexando película ===")
    print(indexar_pelicula_local("Iron Man"))
