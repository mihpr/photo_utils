"""
"""

import os

CLEAN_ROOT = os.path.realpath(r"F:\Photo_archive_IntelPhoto")

CLEAN_LIST = [
    "ZbThumbnail.info",
    "Thumbs.db",
    ".picasa.ini"
]

cleaned_cnt = 0
processed_cnt = 0
for path, directories, files in os.walk(CLEAN_ROOT):
    for file in files:
        processed_cnt += 1
        if file in CLEAN_LIST:
            file_realpath = os.path.join(os.path.realpath(path), file)
            print ("cleaning file_realpath = [%s]" % file_realpath)
            os.remove(file_realpath)
            cleaned_cnt += 1

print ("\n\n\n")

print ("Processed [%d] files in total." % processed_cnt)
print ("Cleaned [%d] files in total." % cleaned_cnt)







