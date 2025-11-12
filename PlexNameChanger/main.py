import IMDBpy
import ServerManager as SM
import RenameProyections as RP
import os

#Ruta al directorio HomeTV
mainPath = "/DiscoDuro/HomeTV/"
#obtengo la lista de deseados y la separo por lineas
ListaDeseados = SM.getListaDeseados().split("\n")

def isVideo(name):
    """Comprueba si un archivo es un video por su extensión"""
    isVideoBool = False
    formats = ["mkv","mp4"]
    i = 0
    while not name.endswith(formats[0]):
        i = i + 1
    if i < len(formats):
        isVideoBool = True
    return(isVideoBool)

def getUnnamed(Path = f'{mainPath}Movies/'):
    """obtiene todos los archivos no correctamente renombrados de un directorio y devuelve un array con todos ellos. Solo funciona con pelis y series"""
    movies = []
    for f in os.getdir(Path):
        if not (f.endswith("Movies") or f.endswith("Series"))
            if isVideo(f):
                movies = movies + [f]
            elsif os.isdir(f):
                movies = movies * [getmovies(f'{Path}f')]
    return(movies)


def getData(ListaDeseados):
    """Funcion de cara al servidor"""
    for i in range(len(ListaDeseados)):
        #obtengo lo que guarda el servidor "nombreCustom - imdbID - Movies" o "nombreSerie - imdbID - Series"
        media = ListaDeseados[i]
        mediaParts = media.split[" - "]
        #detecto si es una serie o una pelicula
        if mediaParts[len(mediaparts)-1] == "Series":
            #si es una serie => CREO CARPETA PARA EL USUARIO
            seriesFolderPath = f'{mainPath}Series/{mediaParts}'
            os.mkdir(seriesFolderPath)

            #Obtengo los datos de los episodios y los guardo en un txt en la caroeta anterior
            episodes = IMDBpy.getSeries(mediaParts[1])
            #primero obtengo los datos de una vez con un for
            episodesInText = ""
            for ep in episodes:
                    episodesInText = f'{episodesInText}\n{ep}'
            #luego los guardo en el fichero
            open(f'{media}.txt',"w").write(episodesInText)

        elsif mediaParts[len(mediaparts)-1] == "Movies":
            #aqui es más simple: obtengo y guardo en el txt generico de la carpeta "Movies"
            MovieCode = IMDBpy.getPeli(mediaParts[1])
            open(f'{mainPath}Movies/ListaDeseados.txt',"w").write(MovieCode)

def showMenu(dataArray,text = "Escoge (0 para abortar): "):
    """Función generica para preguntar al usuario por opciones"""
    i = 0
    for i in range(len(dataArray)):
        print(f'{i+1}.:{dataArray[i]}')
    return(int(input(text)))

def assignMovies():
    """Detecta todas las pelicuals sin nombre de la carpeta HomeTV/Movies y pregunta al usuario, por medio de la funcion showMenu, cual corresponde con que nombre de la lista de deseados"""
    noAbort = True
    movies = open(f'{mainPath}Movies/ListaDeseados.txt',"r").read().split("\n")
    possibilities = getUnnamed()
    i=0
    UInput = showMenu("Cual quieres asignar (0 para abortar): ")
    if UInput not 0:
        Movie = possibilities[UInput - 1]
        UInput = showMenu(movies,"Cual es {Movie} (0 para abortar): ")
        f = movies[UInput-1]
        if UInput not 0:
            noAbort = True
            RP.renameAssign(f'{mainPath}/Movies/proyectios.txt',f,Movie)
    return(noAbort)


def detectEpisodes(SeriesDir):
    """Busca todos los archivos de una carpeta de serie que no hayan sido renombrados y detecta si tienen codigos de episodio, devolviendo un diccionario con la forma {episodeCode:pathToFile}"""
    episodeAssign = {}
    patrones = [
        r'season[^\d]*(\d+)[^\d]*episode[^\d]*(\d+)',  # season X episode X
        r's(\d{1,2})e(\d{1,2})',                       # s01e01
        r's(\d{1,2})[^\w]?e(\d{1,2})',                 # s1e1
        r'(\d{1,2})x(\d{1,2})',                       # 1x01
        r'(\d{1,2})\s*-\s*(\d{1,2})'
    ]
    fEps = getUnnamed(SeriesDir)
    for fEp in fEps:
        fEp = fEp.lower().replace("_", " ").replace(".", " ")
        for patron in patrones:
            match = re.search(patron, nombre_archivo)
            if match:
                episodeCode = match.group(1).zfill(2), match.group(2).zfill(2)
                episodeAssign = episodeAssign + {episodeCode:fEp}
    return(episodeAssign)


def createEpisodeCode(episode):
    """Toma un objeto episode del .ttl de IMDB y saca datos para crear el PMSname"""
    return(f'{episode["ParentName"]} - {episode["EpisodeCode"]} - {episode["primaryTitle"]} - SDQ - {episode["tConst"]} - Series')


def assignSeries(SeriesDir):
    """Detecta automaticamente todos los episodios de una carpeta de una serie y los
añade automaticamente a la lista de assignments de esa carpeta"""
    eps = open(seriesDir,"r").read().split("\n")
    lenEps = len(eps)
    fEps = detectEpisodes(SeriesDir)
    for fEp in fEps.keys():
        i = 0
        while not eps[i]["EpisodeCode"] == fEp:
            i = i + 1
        if i < lenEps:
            RP.renameAssign(SeriesDir,fEp,createEpisodeCode(eps[i]))
            eps.pop(i)
        else:
            print(f'No se puede asignar archivo {fEp}')



def main():
    """Función de cara al usuario, UI principal"""
