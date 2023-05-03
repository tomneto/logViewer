import numpy as np

def fileLinesReader(path):
    with open(path, 'r') as file:
        content = file.readlines()
        file.close()
    return content
