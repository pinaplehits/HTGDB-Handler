from configparser import ConfigParser
import csv
from hashlib import new
import os
import shutil

config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)

#Configuration variables
fields = ['SHA256', 'Path', 'SHA1', 'MD5', 'CRC32', 'Size']
path = config['local']['directory']

def populate_list():
    with open(path, newline = '') as file:                                                                                          
        csv_reader = csv.reader(file, delimiter='\t') 
        csv_list = list(csv_reader) 
    return csv_list

def single_file_db():
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

def new_file(_filename, _extension, _delimiter):
    with open(f'{_filename}.{_extension}', 'w', newline = '') as file:
        csvwriter = csv.writer(file, delimiter = _delimiter)
        #csvwriter.writerow(fields)
        csvwriter.writerows(single_file_db())

def get_extensions():
    file_extension = set()
    
    for i in range(len(data)):
        split_text = os.path.splitext(os.path.basename(data[i][1]))
        file_extension.add(split_text[1].lower())
    
    print(sorted(file_extension))

    return sorted(file_extension)

def main():
    global data
    data = populate_list()

    get_extensions()
    new_file('Super EverDrive & SD2SNES SMDB', 'txt', '\t')
    data.clear()

main()