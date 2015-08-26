import pprint
import os
import glob
import sys

# python ../scripts/cat_blast_files.py ~/Code/cache_server/files/ chk > all.chk

os.chdir(sys.argv[1])
for file in glob.glob("*."+sys.argv[2]):
    file_id = os.path.splitext(file)[0]
    print(">>>START FILE: "+file_id+"."+sys.argv[2])
    with open(file) as infile:
        for line in infile:
            line = line.strip()
            print(line)
    print(">>>STOP FILE: "+file_id+"."+sys.argv[2])
