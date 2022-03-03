from configparser import ConfigParser
import csv
import os
import shutil

config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)

print(config['local']['directory'])

fields = ['SHA256', 'Path', 'SHA1', 'MD5', 'CRC32', 'Size']
fileExtension = []

path = config['local']['directory']

with open(path, newline = '') as games:                                                                                          
    game_reader = csv.reader(games, delimiter='\t') 
    data = list(game_reader) 
    
    #Print number of iterations in the SMDB file
    #print(len(data))

    #Print first and last object in list
    #print(data[0])
    #print(data[-1])

    #print(data[1][0])

    #Print the number of columns in the row
    #print(len(data[0]))
    
    #Print just the filename is splitted from the complete path
    #print(os.path.basename(data[6058][1]))
    
    """split_text = os.path.splitext(os.path.basename(data[6058][1]))
    file_name = split_text[0]
    file_extension = split_text[1]
    print(file_name)
    print(file_extension)"""

    """for i in data:
        if len(i) != 6:
            print(len(i))"""
    
    newdata = []
    newdata.append(data[0])
    x = 1
    
    for i in range(len(data)):
        write = True
        for j in range(len(newdata)):
            if newdata[j][0] == data[i][0]:
                write = False
                break
        if write:
            x += 1
            newdata.append(data[i])
            print(newdata[-1])
    
    print(x)
    print(len(data))
    print(len(data) - x)

with open('Super EverDrive & SD2SNES SMDB.txt', 'w', newline = '') as f:
      
    # using csv.writer method from CSV package
    write = csv.writer(f, delimiter = '\t')
      
    #write.writerow(fields)
    write.writerows(newdata)
