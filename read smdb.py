import csv

fields = ['SHA256', 'Path', 'SHA1', 'MD5', 'CRC32', 'Size']

path = r'\\RETROSMB\retronas\repos\MiSTer FPGA\Hardware-Target-Game-Database\EverDrive Pack SMDBs\Super EverDrive & SD2SNES SMDB.txt'

with open(path, newline = '') as games:                                                                                          
    game_reader = csv.reader(games, delimiter='\t') 
    data = list(game_reader) 
    
    print(len(data))

    print(data[0])
    print(data[-1])

    print(data[0][1])
    print(len(data[0]))

with open('Super EverDrive & SD2SNES SMDB.csv', 'w', newline = '') as f:
      
    # using csv.writer method from CSV package
    write = csv.writer(f)
      
    write.writerow(fields)
    write.writerows(data)
