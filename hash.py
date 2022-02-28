import os
import hashlib

path = r"C:\Users\pinap\Downloads\Silent Hill 2 [NTSC] [Es,Ja,Fr,De,En,It] [GREATEST HITS]\SLUS_202.28.Silent Hill 2.iso"

file_size = os.path.getsize(path)
print("File Size is :", file_size, "bytes")

md5 = hashlib.md5()
sha1 = hashlib.sha1()

listHashObject = [md5, sha1]

for hashObject in listHashObject:
    with open(path, "rb") as openedFile:
        for line in openedFile:
            hashObject.update(line)
        print('{}: {}'.format(hashObject.name, hashObject.hexdigest()))