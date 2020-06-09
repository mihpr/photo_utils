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
SOURCE_ROOT = os.path.realpath("This PC\D7500\Removable storage")
DEST_ROOT = os.path.realpath("D:\Photo_D7500\009")


####################################################################################################

import exifread
import os.path
import shutil

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
for path, directories, files in os.walk(SOURCE_ROOT):
    for file in files:
        # print ('found %s' % os.path.join(path, file))

        src_realpath = os.path.join(os.path.realpath(path), file)
        # print ("date", get_date(path_name))
        
        date = get_date(src_realpath)
        if date is not None:
            year, month, day = date       
            # Year_Month_Day
            dest_dir = os.path.join(DEST_ROOT, year, month, "%s_%s_%s" % (year, month, day))
            photo_with_date_cnt += 1
        else:
            dest_dir = os.path.join(DEST_ROOT, "unknown_date")
            
        dest_file = os.path.join(dest_dir, file)
        
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)      
        #os.rename(path_name, dest_file)
        try:
            if date is not None:
                print ("Copying [%s-%s-%s] from [%s]" % (year, month, day, src_realpath))
            else:
                print ("Copying from [%s]" % (src_realpath,))
            shutil.copy(src_realpath, dest_file)
            photo_cnt += 1
        except IOError as e:
            print("Unable to copy file. %s" % e)
        except:
            print("Unexpected error:", sys.exc_info())

print ("\n\n\n")

print ("Processed [%d] files in total." % photo_cnt)
print ("Date was detected for [%d] photoes." % photo_with_date_cnt)
print ("Date was NOT detected for [%d] files." % (photo_cnt - photo_with_date_cnt))





