from configparser import ConfigParser
import csv
import enum
import os
import glob
import git
import re

#Configuration variables
fields = ['SHA256', 'Path', 'SHA1', 'MD5', 'CRC32', 'Size']

def populate_list(_path):
    with open(str(_path), newline = '') as file:                                                                                          
        csv_reader = csv.reader(file, delimiter='\t') 
        csv_list = list(csv_reader) 
    return csv_list

def single_file_db(_data):
    dataset = set([item[0] for item in _data])

    if len(dataset) == len(_data):
        print("SMDB not reduced")
        return _data

    newdata = []

    for sublist_data in _data:
        if not dataset: break

        if sublist_data[0] in dataset:
            dataset.remove(sublist_data[0])
            newdata.append(sublist_data)
  
    print(f'SMDB reduced from {len(_data)} to {len(newdata)} files')

    return newdata

def new_file(_path, _delimiter, _data):
    with open(_path, 'w', newline = '') as file:
        csvwriter = csv.writer(file, delimiter = _delimiter)
        #csvwriter.writerow(fields)
        csvwriter.writerows(_data)

def get_extensions(_data):
    file_extension = set()
    
    for sublist_data in _data:
        split_text = os.path.splitext(os.path.basename(sublist_data[1]))
        file_extension.add(split_text[1].lower())

    """for i in range(len(_data)):
        split_text = os.path.splitext(os.path.basename(_data[i][1]))
        file_extension.add(split_text[1].lower())"""
    
    print(sorted(file_extension))

    return sorted(file_extension)

def drop_first_folder(_path):
    _path = _path.split('/', 1)
    return _path[1]

def populate_files(_files = '*'):
    data = [x for x in glob.glob(_files)]
    return data.sort(key = str.lower)

def git_head():
    repo = git.Repo(search_parent_directories=True)
    sha1 = repo.head.object.hexsha

    return sha1

#Load all configs and return it to list
def load_config():
    config_file = 'config.ini'
    config = ConfigParser()
    config.read(config_file)
    
    return config['local']['orig_smdb'], config['local']['new_smdb']

def re_files(_data, _regularexpresion):
    for index, value in enumerate(_data): _data[index] = re.split(_regularexpresion, value)
    return _data

def remove_files(_data, _filename, _sha1, i):
    filename = f'{_data[i][0]}_{_data[i][1]}.txt'

    for sublist_data in _data:
        if sublist_data[0] == _filename:
            if sublist_data[1] != _sha1:
                os.remove(filename) 
                print(f'File {filename} removed')
                return
            if sublist_data[1] == _sha1:
                return
    """for j in range(len(_data)):
        if _data[j][0] == _filename:
            if _data[j][1] != _sha1:
                os.remove(filename) 
                print(f'File {filename} removed')
                return
            if _data[j][1] == _sha1:
                return"""

def main():
    #Load config in file .ini
    orig_smdb, new_smdb = load_config()

    #Set path for the workplace
    root = os.path.normpath(os.getcwd())
    repos_path = os.path.dirname(root)
    path_smdb = os.path.normpath(os.path.join(repos_path, orig_smdb))

    #Get SMDB text files and the SHA-1 git head from the repo
    os.chdir(path_smdb)
    smdb_list = populate_files('*.txt')
    sha1 = git_head()
    
    #Set the working directory to the current project
    os.chdir(root)
    os.chdir(os.path.basename(new_smdb))
    
    path_contains_files = False

    if len(os.listdir(os.getcwd())) != 0:
        actual_files = populate_files('*.txt')
        actual_files = re_files(actual_files, '_|\.txt')

        actual_sha1 = set([item[1] for item in actual_files])
        print(actual_sha1)
        path_contains_files = True
    
    for sublist_smdb in smdb_list:
    #for i in range(len(smdb_list)):
        split_text = os.path.splitext(sublist_smdb)
        filename = f'{split_text[0]}_{sha1}.txt'

        if os.path.exists(filename):
                print(f'Filename {filename} already exists')
                continue    
        
        """if path_contains_files:
            if len(actual_files) < i:
                remove_files(actual_files, split_text[0], sha1, i)"""  

        smdb_location = os.path.join(path_smdb, sublist_smdb)
        data = populate_list(smdb_location)
        get_extensions(data)

        print(f'Creating {filename} file...')
        new_file(filename, '\t', 
                single_file_db(data))
        print(f'File {filename} is created',) 

main()