import csv
import os

fields = ['SHA256', 'Path', 'SHA1', 'MD5', 'CRC32', 'Size']
fileExtension = []

path = r'\\RETROSMB\retronas\repos\MiSTer FPGA\Hardware-Target-Game-Database\EverDrive Pack SMDBs\Super EverDrive & SD2SNES SMDB.txt'

with open(path, newline = '') as games:                                                                                          
    game_reader = csv.reader(games, delimiter='\t') 
    data = list(game_reader) 
    
    #Print number of iterations in the SMDB file
    #print(len(data))

    #Print first and last object in list
    #print(data[0])
    #print(data[-1])

    #print(data[6058][1])

    #Print the number of columns in the row
    #print(len(data[0]))
    
    #Print just the filename is splitted from the complete path
    print(os.path.basename(data[6058][1]))

    split_tup = os.path.splitext(os.path.basename(data[6058][1]))
    
    #Print file without extension
    #Print file extension
    print(split_tup[0])
    print(split_tup[1])

with open('Super EverDrive & SD2SNES SMDB.csv', 'w', newline = '') as f:
      
    # using csv.writer method from CSV package
    write = csv.writer(f)
      
    write.writerow(fields)
    write.writerows(data)
