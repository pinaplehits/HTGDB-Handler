import csv
import glob

path = r'\\RETROSMB\retronas\repos\MiSTer FPGA\Hardware-Target-Game-Database\EverDrive Pack SMDBs\Super EverDrive & SD2SNES SMDB.txt'

with open(path, newline = '') as games:                                                                                          
    game_reader = csv.reader(games, delimiter='\t')
    data = list(game_reader)

    """newlist = [x for x in glob.glob("*.txt")]
    newlist.sort(key=str.lower)"""
        
    print(data[2])