import os
import glob
from re import M
from typing import List

diskPath = '/media/pi/RetroNAS/'
repoFolder = 'repos/MiSTer FPGA/Hardware-Target-Game-Database/'
smdbFolder = 'EverDrive Pack SMDBs/'
unorganizedFolder = 'romimport/'
missingFolder = 'missingroms/'
outputFolder = 'mister/games/'
scriptName = 'verify_pack.py'

scripPath = diskPath + repoFolder + scriptName
unorganizedPath = diskPath + unorganizedFolder
smdbPath = diskPath + repoFolder + smdbFolder
outputPath = diskPath + outputFolder
missingPath = diskPath + missingFolder

def selectionScreen(list, message):
    for (i, item) in enumerate(list):
        print(i, item)
    
    x = int(input(message))

    return x

def createSmdbPath():
    global smdbPath, missingPath

    os.chdir(smdbPath)

    newlist = [x for x in glob.glob("*.txt")]
    newlist.sort(key=str.lower)

    index = selectionScreen(newlist, 'Select one SMDB file: ')

    smdbFilename = newlist[index]
    smdbPath += smdbFilename
    missingPath += smdbFilename

def createOutputPath():
    global outputPath
    
    newlist = [x.name for x in os.scandir(outputPath) if x.is_dir()]
    newlist.sort(key=str.lower)

    index = selectionScreen(newlist, 'Select one folder core: ')

    misterCoreName = newlist[index]
    outputPath += misterCoreName

createSmdbPath()

createOutputPath()

print(f"python3 '{scripPath}' -f '{outputPath}' -d '{smdbPath}' -m '{missingPath}' -x")
os.system(f"python3 '{scripPath}' -f '{outputPath}' -d '{smdbPath}' -m '{missingPath}' -x")
input("Press any key to continue...")