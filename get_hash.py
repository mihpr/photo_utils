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
# SOURCE_ROOT = os.path.realpath("D:\Photo_archive_001")
SOURCE_ROOT = os.path.realpath("E:\Photo_archive_001")
# SOURCE_ROOT = os.path.realpath("D:\Photo_D7500\print2")
# SOURCE_ROOT = os.path.realpath("D:\Photo_D7500\Jury")


DEST_ROOT = SOURCE_ROOT
HASH_ALGORITHM = SHA256

####################################################################################################
import hashlib
import json
import datetime
import posixpath 
# import npath

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
        if file_extension.upper() == ".JSON":
            continue
        src_abspath = os.path.join(os.path.abspath(path), file)
        src_relpath = os.path.relpath(src_abspath, SOURCE_ROOT) # path relative to root, which is easy to compare between different drives"
        hash = get_file_hash(src_abspath, HASH_ALGORITHM)
        print ("Hash [%s], file [%s]" % (hash, src_abspath))
        hashes_lst.append({"posixpath": posixpath.normpath(src_relpath), "hash": hash})
index["file_data"] = hashes_lst

j = json.dumps(hashes_lst)
now_txt = now.strftime("%Y-%m-%d_%H-%M-%S")
hashes_file = os.path.join(DEST_ROOT, "hashes_" + now_txt + ".json")
print ("File with hashes [%s]" % hashes_file)
with open(hashes_file, "w") as f:
    json.dump(index, f, indent=4)