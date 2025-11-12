def alphabetOrder(word1,word2):
    firstIsGreater = 0
    alphabet = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
    length = len(word1)
    if len(word1) > len(word2):
        length = len(word2)

    for i in length:
        letter1 = word1[i]
        letter2 = word2[i]
        if letter1 != letter2:
            if (letter1 in alphabet) and (letter2 in alphabet):
                letter1 = alphabet.index(letter1)
                letter2 = alphabet.index(letter2)
            if letterN1 > letterN2:
                firstIsGreater = 1
            else

    return(firstIsGreater)


def Busqueda(Name,dataBase):
    simpName = Name.lowecase()
    simpName = simpName.split(" ")
    results = []
    for data in dataBase:
        closeness = 0
        for word in simpName:
            if word in data:
                closeness = closeness + len(word)
        if closeness > 2:
            dataCloseness = [data,closeness]
            i = 0
            while (i in len(results)) and (result[1] <= closeness) and (alphabetOrder(data,result[0])):
                i = i + 1
            if i > len(results):
                results = results + [dataCloseness]
            size = len(results)
            results = results + [results[size]-1]
            for j in range(i + 1, size - 1):
                results[j+1] = results[j]
            results[i] = dataCloseness

def encontrarMedia(nombre,imdb):
    simpName = Name.lowecase()
    simpName = simpName.split(" ")
    results = []
    for media in imdb:
        mediaName = media["primaryTitle"]
        closeness = 0
        for word in simpName:
            if word in mediaName:
                closeness = closeness + len(word)
        if closeness > 2:
            dataCloseness = [mediaName,closeness]
            i = 0
            while (i in len(results)) and (result[1] <= closeness) and (alphabetOrder(mediaName,result[0])):
                i = i + 1
            if i > len(results):
                results = results + [dataCloseness]
            size = len(results)
            results = results + [results[size]-1]
            for j in range(i + 1, size - 1):
                results[j+1] = results[j]
            results[i] = dataCloseness
    return(results)
