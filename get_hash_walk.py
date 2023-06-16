"""
Copy this script into HOME_DIR, which is the directory containing your archives HOME_DIR.
It might be the root of your removable drive. Edit settings and run the script:

$ python get_hash_walk.py
"""

import os

"""
Settings
"""
PHOTO_UTILS_DIR = os.path.abspath(r"D:/git/photo_utils")
GET_HASH_PY = os.path.join(PHOTO_UTILS_DIR, "get_hash.py")
HOME_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_LIST = (
    # "root 1",
    # "root 2",
    # "root 3",
    # "...",
    # "root N"
)

"""
End of settings
"""

for root_dir in ROOT_LIST:
    root_dir_abs_path = os.path.join(HOME_DIR, root_dir)
    print("Getting hashes for '%s'..." % root_dir_abs_path)
    os.system("python %s %s" % (GET_HASH_PY, root_dir_abs_path))
    print("Getting hashes for '%s' done." % root_dir_abs_path)