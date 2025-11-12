import os
import re
import csv
import urllib.request
import json




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


def cargar_title_episodes(path='imdb_data/title.episode.tsv'):
    return(pd.read_csv(IMDB_DIR / "title.episode.tsv", sep="\t", dtype=str, low_memory=False))



def cargar_title_basics(path='imdb_data/title.basics.tsv'):
    titulos = {}
    with open(path, encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            titulos[row['tconst']] = row['primaryTitle']
    return titulos


def getPeli(IMDBid):
    peli = cargar_title_basics()[IMDBid]
    return(f'{peli['primaryTitle']} - S01E01 - {peli['primaryTitle']} - SDQ - {peli['tconst']} - Movies')

def getSeries(IMDBid):
    series = cargar_title_basics()[IMDBid]
    episodes = cargar_title_episodes()

    eps = [episodes[episodes["parentTconst"] == serie_id]
    return(eps)

















