import os

def relativePath(path):
    return os.path.join(os.path.dirname(__file__), path)

def splitDict(input, chunkSize):
    res = []
    new_dict = {}
    for k, v in input.items():
        if len(new_dict) < chunkSize:
            new_dict[k] = v
        else:
            res.append(new_dict)
            new_dict = {k: v}
    res.append(new_dict)
    return res

def splitList(input, chunkSize):
    result = list()
    newList = list()
    for v in input:
        if len(newList) < chunkSize:
            newList.append(v)
        else:
            result.append(newList)
            newList = [v]
    result.append(newList)
    return result

async def readFile(filename):
    with open(filename, 'r') as file:
        content = file.read()
        file.close()
    return content