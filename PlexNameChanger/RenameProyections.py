def renameAssign(filePath,path,newName):
    open(filePath,"w").write(f'{path} => newname')

def renamer(filePath):
    paths = open(filePath,"r").read().split(" => ")
    path1 = paths[0]
    a = path1.split("/")
    a[len(path2)-1] = paths[1]
    path2 = ""
    for i in a:
        path2 = f'{a}/{i}'
    os.rename(path1,path2)
