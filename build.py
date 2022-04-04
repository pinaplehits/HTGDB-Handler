from cgitb import text
import os
import glob
from configparser import ConfigParser
from pathlib import Path
from re import I

#Load all configs and return it to list
def load_config():
    config_file = 'config.ini'
    config = ConfigParser()
    config.read(config_file)
    
    return config['local']['orig_smdb'], config['local']['new_smdb']

def populate_files(_files = '*'):
    data = [x for x in glob.glob(_files)]
    data.sort(key = str.lower)

    return data

def selection_screen(list, message):
    for index, value in enumerate(list):
        print(index, value)

    return int(input(message))

def script_path(_path):
    x = int(input('0. Build pack\n1. Verify pack\nSelect a python script: '))
    
    if x:
        return os.path.join(os.path.dirname(_path), 'verify_pack.py'), x
    else:
        return os.path.join(os.path.dirname(_path), 'build_pack.py'), x

def database_folder(_path):
    os.chdir(_path)
    smdb_list = populate_files('*.txt')
    index = selection_screen(smdb_list, 'Select one SMDB file: ')
    
    return smdb_list[index]

def destination_folder(_path):
    x = int(input('0. MiSTer\n1. Collection\n2. Single file\nSelect a folder destination: '))
    if x == 0:
        outputPath = os.path.join(_path, 'mister', 'games')
        
        directory_mister = [x.name for x in os.scandir(outputPath) if x.is_dir()]
        directory_mister.sort(key=str.lower)
        
        index = selection_screen(directory_mister, 'Select one folder core: ')

        return os.path.join(outputPath, directory_mister[index])
    elif x == 1:
        return os.path.join(_path, 'Collection')
    elif x == 2:
        return os.path.join(_path, 'Collection', 'Single files SMDB')

def build_script(_cmd):
    input(_cmd)
    os.system(_cmd)
    input("Press any key to continue...")

def verify_script(_cmd):
    input(_cmd)
    os.system(_cmd)
    input('Press any key to continue...')

def main():
    #Load config in file .ini
    orig_smdb, new_smdb = load_config()

    source_repo = os.path.normpath(os.getcwd())
    root = Path(__file__).parents[2]
    repos_path = os.path.dirname(source_repo)
    path_smdb = os.path.normpath(os.path.join(repos_path, orig_smdb))
    scripPath, x = script_path(path_smdb)
    folder = os.path.splitext(database_folder(path_smdb))[0]
    smdbPath = os.path.join(path_smdb, f'{folder}.txt')
    missingPath = os.path.join(root, 'missingroms', f'{folder}.txt')
    outputPath = os.path.join(destination_folder(root), folder)
    
    if x == 0:
        unorganizedPath = os.path.join(root, 'romimport')
        build_cmd = f"python3 '{scripPath}' --input_folder '{unorganizedPath}' --database '{smdbPath}' --output_folder '{outputPath}' --missing '{missingPath}' --skip_existing --drop_initial_directory --file_strategy hardlink"

        build_script(build_cmd)
    else:
        verify_cmd = f"python3 '{scripPath}' --folder '{outputPath}' --database '{smdbPath}' --mismatch '{missingPath}' --drop_initial_directory"
        
        verify_script(verify_cmd)

main()