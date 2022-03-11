from configparser import ConfigParser
from hashlib import new
import csv
from json import load
import os
import glob

config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)

#Configuration variables
fields = ['SHA256', 'Path', 'SHA1', 'MD5', 'CRC32', 'Size']
path = config['local']['directory']

def root_folder(_current_directory):
        root = os.path.dirname(_current_directory)
        root = root.replace(os.sep, '/')
        print(root)

        return root

def populate_list(_path):
    with open(_path, newline = '') as file:                                                                                          
        csv_reader = csv.reader(file, delimiter='\t') 
        csv_list = list(csv_reader) 
    return csv_list

def single_file_db(_data):
    newdata = []
    newdata.append(_data[0])

    for i in range(len(_data)):
        write = True
        for j in range(len(newdata)):
            if newdata[j][0] == _data[i][0]:
                write = False
                if len(newdata[j]) != len(_data[i]):
                    print(len(newdata[j]), len(_data[i]))
                break
        if write:
            newdata.append(_data[i])

    print(f'SMDB reduced from {len(_data)} to {len(newdata)} files')

    return newdata

def new_file(_path, _delimiter, _data):
    with open(_path, 'w', newline = '') as file:
    #with open('//RETROSMB/retronas/repos/HTGDB-Handler/No Duplicates SMDBs/new.txt', 'w', newline = '') as file:
        csvwriter = csv.writer(file, delimiter = _delimiter)
        #csvwriter.writerow(fields)
        csvwriter.writerows(_data)

def get_extensions(_data):
    file_extension = set()
    
    for i in range(len(_data)):
        split_text = os.path.splitext(os.path.basename(_data[i][1]))
        file_extension.add(split_text[1].lower())
    
    print(sorted(file_extension))

    return sorted(file_extension)

def drop_first_folder(_path):
    _path = _path.split('/', 1)
    return _path[1]

def get_smdb(root, origin_path):
    dir_smdb = root + (config['local']['SMDBs'])
    os.chdir(dir_smdb)
    smdb_list = [x for x in glob.glob("*.txt")]
    smdb_list.sort(key = str.lower)
    
    os.chdir(origin_path)

    return smdb_list

def main():
    current_directory = os.getcwd()
    root = root_folder(current_directory)
    smdb_list = get_smdb(root, current_directory)
    
    for i in range(len(smdb_list)):
        #print(smdb_list[i])
        path = root + (config['local']['single_SMDBs']) + smdb_list[i]
        dir_smdb = root + (config['local']['SMDBs']) + smdb_list[i]
        data = populate_list(dir_smdb)
        get_extensions(data)
        print(path)
        new_file(path, '\t', 
                single_file_db(data))
        data.clear()

    #get_extensions(data)
    #print(drop_first_folder('SD2SNES/1 US - A-E/2020 Super Baseball (USA).sfc'))
    

main()