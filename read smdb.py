from configparser import ConfigParser
import csv
from hashlib import new
import os
import shutil

config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)

print(config['local']['directory'])

fields = ['SHA256', 'Path', 'SHA1', 'MD5', 'CRC32', 'Size']
fileExtension = []

path = config['local']['directory']

def populate_list():
    with open(path, newline = '') as file:                                                                                          
        csv_reader = csv.reader(file, delimiter='\t') 
        data = list(csv_reader) 
    return data

def single_file_db():
    data = populate_list()

    newdata = []
    newdata.append(data[0])

    for i in range(len(data)):
        write = True
        for j in range(len(newdata)):
            if newdata[j][0] == data[i][0]:
                write = False
                if len(newdata[j]) != len(data[i]):
                    print(len(newdata[j]), len(data[i]))
                break
        if write:
            newdata.append(data[i])

    print(f'SMDB reduced from {len(data)} to {len(newdata)} files')

    return newdata

def new_file(filename, extension, _delimiter):
    with open(f'{filename}.{extension}', 'w', newline = '') as file:
        csvwriter = csv.writer(file, delimiter = _delimiter)
        #csvwriter.writerow(fields)
        csvwriter.writerows(single_file_db())

new_file('Super EverDrive & SD2SNES SMDB', 'txt', '\t')

"""
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

split_text = os.path.splitext(os.path.basename(data[6058][1]))
file_name = split_text[0]
file_extension = split_text[1]
print(file_name)
print(file_extension)

for i in data:
    if len(i) != 6:
        print(len(i))
    """