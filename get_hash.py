"""
This scropt gets file hashes

How to use this sctipt:
TODO

The script was tested with Python 3.8.1
"""

READ_BLOCK_SIZE = 4096
MD5 = "MD5"
SHA256 = "SHA256"
SHA512 = "SHA512"

import os
SOURCE_ROOT = os.path.realpath("D:\Photo_archive_001")
DEST_ROOT = SOURCE_ROOT
HASH_ALGORITHM = SHA256

####################################################################################################
import hashlib
import json
import datetime

def get_file_hash(fname, hash_type):
    if hash_type == MD5:
        hash = hashlib.md5()
    elif hash_type == SHA256:
        hash = hashlib.sha256()
    elif hash_type == SHA512:
        hash = hashlib.sha512()
    else:
        raise Exception("Undefined alogrithm")
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(READ_BLOCK_SIZE), b""):
            hash.update(chunk)
    return hash.hexdigest()

print ("Saving hashes for files at path [%s]..." % SOURCE_ROOT)

now = datetime.datetime.now()
index = {"algorithm": HASH_ALGORITHM, "datetime": now.strftime("%Y:%m:%d %H:%M:%S")}
hashes_lst = []
for path, directories, files in os.walk(SOURCE_ROOT):
    for file in files:
        filename, file_extension = os.path.splitext(file)
        print ("[%s] [%s]" % (filename, file_extension))
        if file_extension.upper() == ".JSON":
            continue
        src_realpath = os.path.join(os.path.realpath(path), file)
        hash = get_file_hash(src_realpath, HASH_ALGORITHM)
        
        print ("Hash [%s], file [%s]" % (hash, src_realpath))
        hashes_lst.append({"path": src_realpath, "hash": hash})
index["file_data"] = hashes_lst

j = json.dumps(hashes_lst)
now_txt = now.strftime("%Y-%m-%d_%H-%M-%S")
hashes_file = os.path.join(DEST_ROOT, "hashes_" + now_txt + ".json")
print ("File with hashes [%s]" % hashes_file)
with open(hashes_file, "w") as f:
    json.dump(index, f, indent=4)