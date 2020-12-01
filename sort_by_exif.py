"""
The script copyies photoes and sorts the files by date based on EXIF data.
It seems that it can get EXIF data out of JPEG and RAW files.
In case the exif data cannot be detected, it puts the file in to a special 'unknown_date' folder.

How to use this sctipt:
1) Set source and destination paths below.
2) Run the script.

The script was tested with Python 3.8.1
"""

import os
import filecmp
SOURCE_ROOT = os.path.realpath(r"D:\Dropbox\Photos\bluetooth")
DEST_ROOT = os.path.realpath(r"D:\Photo_archive_001\SonyEricsson_k750i")

# True:  copy
# False: move
COPY_MODE = True

ARRANGE_YEAR_MONTH =     1
ARRANGE_YEAR_MONTH_DAY = 2

ARRANGE_MODE = ARRANGE_YEAR_MONTH

####################################################################################################

import exifread
import os.path
import shutil
import time

print("SOURCE_ROOT = [%s]" % SOURCE_ROOT)
print("DEST_ROOT = [%s]" % DEST_ROOT)

def get_date(path_name):
    # Open image file for reading (binary mode)
    try:
        with open(path_name, 'rb') as f:
            # Return Exif tags
            tags = exifread.process_file(f)
            DateTimeOriginal = str(tags["EXIF DateTimeOriginal"])
            date, time = DateTimeOriginal.split(" ")
            year, month, day = date.split(":")
            return year, month, day
    except Exception as e:
        print ("Exception [%s] while getging EXIF DateTimeOriginal from file at path [%s]" % (e, path_name))
    except:
        print("Unexpected error:", sys.exc_info())

photo_cnt = 0
photo_with_date_cnt = 0
identical_photo_cnt = 0
photo_with_errors_cnt = 0
for path, directories, files in os.walk(SOURCE_ROOT):
    for file in files:
        # print ('found %s' % os.path.join(path, file))

        src_realpath = os.path.join(os.path.realpath(path), file)
        # print ("date", get_date(path_name))
        
        date = get_date(src_realpath)
        if date is not None:
            year, month, day = date       
            # Year_Month_Day
            if ARRANGE_MODE == ARRANGE_YEAR_MONTH_DAY:
                dest_dir = os.path.join(DEST_ROOT, year, month, "%s_%s_%s" % (year, month, day))
            elif ARRANGE_MODE == ARRANGE_YEAR_MONTH:
                dest_dir = os.path.join(DEST_ROOT, year, month)
            photo_with_date_cnt += 1
        else:
            dest_dir = os.path.join(DEST_ROOT, "unknown_date")
            
        dest_file = os.path.join(dest_dir, file)

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # Check if such file exist
        if os.path.isfile(dest_file):
            # TODO: check if hash is the same
            if filecmp.cmp(src_realpath, dest_file, shallow=False):
                #equal
                print ("File is identical skip [%s-%s-%s] from [%s]" % (year, month, day, src_realpath))
                photo_cnt += 1
                identical_photo_cnt += 1
                continue
            else:
                photo_with_errors_cnt += 1
                #dest_file += "_" + str(time.time())
                filename, file_extension = os.path.splitext(file)
                filename += "_" + str(time.time())
                dest_file = os.path.join(dest_dir, filename + file_extension)

        try:
            if date is not None:
                print ("Copying/moving [%s-%s-%s] from [%s]" % (year, month, day, src_realpath))
            else:
                print ("Copying/moving [%s]" % (src_realpath,))
            if COPY_MODE:
                shutil.copy(src_realpath, dest_file)
            else:
                os.rename(src_realpath, dest_file)
            photo_cnt += 1
        except IOError as e:
            print("Unable to copy file. %s" % e)
        except:
            print("Unexpected error:", sys.exc_info())

print ("\n\n\n")

print ("Processed [%d] files in total." % photo_cnt)
print ("Date was detected for [%d] photoes." % photo_with_date_cnt)
print ("Date was NOT detected for [%d] files." % (photo_cnt - photo_with_date_cnt))
print ("[%d] identical photoes were found ." % (identical_photo_cnt))
print ("Potential errors were found in [%d] photoes ." % (photo_with_errors_cnt))






