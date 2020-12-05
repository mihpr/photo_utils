"""
This scropt gets file hashes

How to use this sctipt

To hash the whole arvhive:
python get_hash2.py path_to_archive

To hash the one specific volume:
python get_hash2.py path_to_archive volume volume_dir_name

The script was tested with Python 3.9
"""
import os
import sys
import hashlib
import json
import datetime
import posixpath
import logging

####################################### Defines ####################################################
MD5 = "MD5"
SHA256 = "SHA256"
SHA512 = "SHA512"

####################################### Config #####################################################

HASH_ALGORITHM = SHA256
READ_BLOCK_SIZE = 4096
LOG_LEVEL = logging.INFO
LOG_ENCODING = "utf-8"

####################################### Globals ####################################################

####################################################################################################

def get_file_hash(fname, hash_type):
    if hash_type == MD5:
        hash = hashlib.md5()
    elif hash_type == SHA256:
        hash = hashlib.sha256()
    elif hash_type == SHA512:
        hash = hashlib.sha512()
    else:
        logging.critical("Undefined alogrithm")
        raise Exception("Undefined alogrithm")
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(READ_BLOCK_SIZE), b""):
            hash.update(chunk)
    return hash.hexdigest()

def save_hashes_for_files(root_dir_abspath, file_abspath_lst, hashes_file_abspath):
    logging.info("Saving hashes files in archive root")
    hashes_lst = []
    for src_abspath in file_abspath_lst:
        src_relpath = os.path.relpath(src_abspath, root_dir_abspath) # path relative to root, which is easy to compare between different drives"
        hash = get_file_hash(src_abspath, HASH_ALGORITHM)
        logging.debug("Processing file [%s]" % (src_abspath))
        print("Processing file [%s]" % (src_abspath))
        hashes_lst.append({"posixpath": posixpath.normpath(src_relpath), "hash": hash})

    logging.info("Saving hashes to file... [%s]" % hashes_file_abspath)
    with open(hashes_file_abspath, "w") as f:
        json.dump(hashes_lst, f, indent=4)
    logging.info("Done [%s]" % hashes_file_abspath)

def save_hashes_for_volume(achive_root_abspath, volume_dir_abspath, hashes_file_abspath):
    logging.info("Saving hashes for directory at path [%s]" % volume_dir_abspath)
    hashes_lst = []
    for path, directories, files in os.walk(volume_dir_abspath):
        for file in files:
            filename, file_extension = os.path.splitext(file)
            if file_extension.upper() == ".JSON":
                continue
            src_abspath = os.path.join(os.path.abspath(path), file)
            src_relpath = os.path.relpath(src_abspath, achive_root_abspath) # path relative to root, which is easy to compare between different drives"
            hash = get_file_hash(src_abspath, HASH_ALGORITHM)
            logging.debug("Processing file [%s]" % (src_abspath))
            print("Processing file [%s]" % (src_abspath))
            hashes_lst.append({"posixpath": posixpath.normpath(src_relpath), "hash": hash})

    logging.info("Saving hashes to file... [%s]" % hashes_file_abspath)
    with open(hashes_file_abspath, "w") as f:
        json.dump(hashes_lst, f, indent=4)
    logging.info("Done [%s]" % hashes_file_abspath)


####################################################################################################

if __name__ == "__main__":
    start_datetime = datetime.datetime.now()
    start_datetime_txt = start_datetime.strftime("%Y-%m-%d__%H-%M-%S")

    if len(sys.argv) < 2:
        print ("Not enough arguments")
        exit(0)
    archieve_root = os.path.abspath(sys.argv[1])
    if not os.path.isdir(archieve_root):
        print("There is no directory: [%s]" % archieve_root)
        exit(0)
    if len(sys.argv) < 3:
        volume_to_hash = None  # hash all volumes
    else:
        volume_to_hash = sys.argv[2]
        if not os.path.isdir(os.path.join(archieve_root, volume_to_hash)):
            print("There is no directory: [%s] in archieve_root [%s]" % (volume_to_hash, archieve_root))
        

    hash_dir_root = os.path.join(os.path.abspath(archieve_root), "hashes__%s" % start_datetime_txt)

    if not os.path.exists(hash_dir_root):
        os.makedirs(hash_dir_root)

    logfile = os.path.join(hash_dir_root, "log.txt")
    logging.basicConfig(
        filename=logfile,
        encoding=LOG_ENCODING,
        level=LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logging.info("Hashing started at: [%s]" % start_datetime_txt)
    logging.info("archieve_root = [%s]" % archieve_root)
    logging.info("hash_dir_root = [%s]" % hash_dir_root)
    logging.info("HASH_ALGORITHM = [%s]" % HASH_ALGORITHM)
    logging.info("READ_BLOCK_SIZE = [%s]" % READ_BLOCK_SIZE)
    if volume_to_hash is None:
        logging.debug("Mode: all volumes in the archive")
        files_and_dirs = [os.path.join(archieve_root, item) for item in os.listdir(archieve_root) if "hashes" not in item]
        directories = [item for item in files_and_dirs if os.path.isdir(item)]
        files = [item for item in files_and_dirs if os.path.isfile(item)]

        for dir_abspath in directories:
            dir = os.path.relpath(dir_abspath, archieve_root)
            hashes_file = os.path.join(hash_dir_root, dir + "_hashes.json")
            save_hashes_for_volume(archieve_root, dir_abspath, hashes_file)
            
        if len(files) > 0:
            hashes_file = os.path.join(hash_dir_root, "files_hashes.json")
            save_hashes_for_files(archieve_root, files, hashes_file)
    else: # specific volume
        logging.debug("Mode: specific volume: [%s]" % volume_to_hash)
        dir_abspath = os.path.join(archieve_root, volume_to_hash)
        dir = volume_to_hash
        hashes_file = os.path.join(hash_dir_root, dir + "_hashes.json")
        save_hashes_for_volume(archieve_root, dir_abspath, hashes_file)

    logging.info("Hashing ended at: [%s]" % datetime.datetime.now().strftime("%Y-%m-%d__%H-%M-%S"))
