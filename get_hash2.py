"""
This scropt gets file hashes

How to use this sctipt:
TODO

The script was tested with Python 3.9
At least Python 3.9 is required
"""
import os
import hashlib
import json
import datetime
import posixpath
import logging
import configparser

start_datetime = datetime.datetime.now()
start_datetime_txt = start_datetime.strftime("%Y-%m-%d_%H-%M-%S")

config = configparser.ConfigParser()
config.read("get_hash.ini")

READ_BLOCK_SIZE = 4096
MD5 = "MD5"
SHA256 = "SHA256"
SHA512 = "SHA512"

VOLUME_ROOT = os.path.realpath(config["GET_HASH"]["volume_root"])
HASH_DIR_ROOT = os.path.join(VOLUME_ROOT, "hashes")
HASH_ALGORITHM = SHA256
DIR_TO_HASH = config["GET_HASH"]["dir_to_hash"]

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
    index = {"algorithm": HASH_ALGORITHM, "datetime": start_datetime.strftime("%Y:%m:%d %H:%M:%S")}
    hashes_lst = []
    for src_abspath in file_abspath_lst:
        src_relpath = os.path.relpath(src_abspath, root_dir_abspath) # path relative to root, which is easy to compare between different drives"
        hash = get_file_hash(src_abspath, HASH_ALGORITHM)
        logging.debug("Processing file [%s]" % (src_abspath))
        print("Processing file [%s]" % (src_abspath))
        hashes_lst.append({"posixpath": posixpath.normpath(src_relpath), "hash": hash})
    index["file_data"] = hashes_lst

    # j = json.dumps(hashes_lst)
    logging.info("Saving hashes to file... [%s]" % hashes_file_abspath)
    with open(hashes_file_abspath, "w") as f:
        json.dump(index, f, indent=4)
    logging.info("Done [%s]" % hashes_file_abspath)

def save_hashes_for_dir(root_dir_abspath, hashes_file_abspath):
    logging.info("Saving hashes for directory at path [%s]..." % root_dir_abspath)
    index = {"algorithm": HASH_ALGORITHM, "datetime": start_datetime.strftime("%Y:%m:%d %H:%M:%S")}
    hashes_lst = []
    for path, directories, files in os.walk(root_dir_abspath):
        for file in files:
            filename, file_extension = os.path.splitext(file)
            if file_extension.upper() == ".JSON":
                continue
            src_abspath = os.path.join(os.path.abspath(path), file)
            src_relpath = os.path.relpath(src_abspath, root_dir_abspath) # path relative to root, which is easy to compare between different drives"
            hash = get_file_hash(src_abspath, HASH_ALGORITHM)
            logging.debug("Processing file [%s]" % (src_abspath))
            print("Processing file [%s]" % (src_abspath))
            hashes_lst.append({"posixpath": posixpath.normpath(src_relpath), "hash": hash})
    index["file_data"] = hashes_lst

    # j = json.dumps(hashes_lst)
    logging.info("Saving hashes to file... [%s]" % hashes_file_abspath)
    with open(hashes_file_abspath, "w") as f:
        json.dump(index, f, indent=4)
    logging.info("Done [%s]" % hashes_file_abspath)

if __name__ == "__main__":
    if not os.path.exists(HASH_DIR_ROOT):
        os.makedirs(HASH_DIR_ROOT)

    logfile = os.path.join(HASH_DIR_ROOT, "log_%s.txt" % start_datetime_txt)
    logging.basicConfig(
        filename=logfile,
        encoding="utf-8",
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if DIR_TO_HASH == "all":
        logging.info("Saving hashes for volume at path [%s]..." % VOLUME_ROOT)
        logging.debug("VOLUME_ROOT = [%s]" % VOLUME_ROOT)
        logging.debug("HASH_DIR_ROOT = [%s]" % HASH_DIR_ROOT)
        logging.debug("HASH_ALGORITHM = [%s]" % HASH_ALGORITHM)
        logging.debug("READ_BLOCK_SIZE = [%s]" % READ_BLOCK_SIZE)
        
        files_and_dirs = [os.path.join(VOLUME_ROOT, item) for item in os.listdir(VOLUME_ROOT) if "hashes" not in item]
        directories = [item for item in files_and_dirs if os.path.isdir(item)]
        files = [item for item in files_and_dirs if os.path.isfile(item)]

        for dir_abspath in directories:
            dir = os.path.relpath(dir_abspath, VOLUME_ROOT)
            hashes_file = os.path.join(HASH_DIR_ROOT, dir + "_hashes_" + start_datetime_txt + ".json")
            save_hashes_for_dir(dir_abspath, hashes_file)
            
        if len(files) > 0:
            hashes_file = os.path.join(HASH_DIR_ROOT, "files_hashes_" + start_datetime_txt + ".json")
            save_hashes_for_files(VOLUME_ROOT, files, hashes_file)
    else:
        dir_abspath = os.path.join(VOLUME_ROOT, DIR_TO_HASH)
        dir = DIR_TO_HASH
        hashes_file = os.path.join(HASH_DIR_ROOT, dir + "_hashes_" + start_datetime_txt + ".json")
        save_hashes_for_dir(dir_abspath, hashes_file)

