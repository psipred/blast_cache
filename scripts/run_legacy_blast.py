import requests
import sys
import hashlib
import subprocess
import shlex
import os.path
from Bio.Blast import NCBIXML
import time
import math
import json
import shutil
# arg 1 input fasta file
# arg 2 output dir
# arg 3 base uri
# arg 4 blast bin path
# arg 6 blast settings string
# arg 5 blast db

#
# python scripts/run_blast.py ./files/P04591.fasta ./files http://127.0.0.1:8000 /scratch0/NOT_BACKED_UP/dbuchan/Applications/ncbi-blast-2.2.31+/bin/ /scratch1/NOT_BACKED_UP/dbuchan/uniref/pdb_aa.fasta -num_iterations 20 -num_alignments 500 -num_threads 2
#
# python scripts/run_blast.py ./files/P04591.fasta ./files http://127.0.0.1:8000 /opt/ncbi-blast-2.5.0+/bin/ /opt/uniref/uniref90.fasta -num_iterations 20 -num_alignments 500 -num_threads 2


def read_file(path):
    seq = ''
    with open(path, 'r') as myfile:
        data = myfile.read()
    for line in data.split("\n"):
        if line.startswith(">"):
            continue
        line = line.rstrip()
        seq += line
    m = hashlib.md5()
    test_hash = m.update(seq.encode('utf-8'))
    return({'seq': seq, 'md5': m.hexdigest()})


def get_num_alignments(path):
    hit_count = 0
    if os.path.isfile(path):
        result_handle = open(path)
        blast_records = NCBIXML.parse(result_handle)
        for record in blast_records:
            if len(record.alignments) > hit_count:
                hit_count = len(record.alignments)
    else:
        eprint("Couldn't get Alignment number")
        exit(1)

    return(hit_count)


def get_pssm_data(path):
    pssm_data = ""
    print(path)
    if os.path.isfile(path):
        with open(path, "r") as myfile:
            pssm_data = myfile.read()
    else:
        eprint("Couldn't get PSSM data")
        exit(1)  # panic

    return(pssm_data)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


fasta_file = sys.argv[1]  # path to input fasta
out_dir = sys.argv[2]  # path to place blast output and PSSM files
base_uri = sys.argv[3]  # ip or URI for the server blast_cache is running on
blast_bin = sys.argv[4]  # path to the blast binary dir
blast_db = sys.argv[5]  # path to blast db location
output_type = sys.argv[6]  # file endsing for PSSM file
blast_settings = " ".join(sys.argv[7:])  # get everything else on the
#                                          commandline make it a string and
#                                          use it as the blast settings
seq_name = fasta_file.split("/")[-1].split(".")[0]
single_file = out_dir+"/"+seq_name+".sing"
fasta_contents = []
with open(fname) as f:
    fasta_contents = f.readlines()
seq_count = fasta_contents.count(">")
if seq_count == 1:
    with open(single_file, 'w') as sing:
        sing.write(file_contents)
else:
    fasta_lines = file_contents.split()
    with open(single_file, 'w') as sing:
        seq_count = 0
        for line in fasta_lines:
            if line.startswith(">"):
                seq_count += 1
            if seq_count == 1:
                sing.write(line.replace("-", ""))


# strings and data structures we need
file_contents = read_file(single_file)

entry_uri = base_uri+"/blast_cache/entry/"
entry_query = entry_uri+file_contents['md5']
i = iter(blast_settings.split())
request_data = dict(zip(i, i))

r = requests.get(entry_query, params=request_data)
print("Cache Response:", r.status_code)
exit()
if r.status_code == 404 and "No Record Available" in r.text:
    print("Running blast")
    cmd = ''
    if output_type == "chk6":
        cmd = blast_bin+"/blastpgp -i "+fasta_file+" -C "+out_dir+"/"+seq_name+"."+output_type+" -d " + \
            blast_db+" -m 7 -o "+out_dir+"/"+seq_name+".xml -R "+out_dir+"/"+seq_name+".chk "+blast_settings
    else:
        cmd = blast_bin+"/blastpgp -i "+fasta_file+" -C "+out_dir+"/"+seq_name+"."+output_type+" -d " + \
            blast_db+" -m 7 -o "+out_dir+"/"+seq_name+".xml "+blast_settings
    print(cmd)
    start_time = time.time()
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.wait()
    with open(out_dir+"/"+seq_name+".pn", 'w') as pn:
        pn.write(out_dir+"/"+seq_name+"."+output_type)
    with open(out_dir+"/"+seq_name+".sn", 'w') as sn:
        sn.write(out_dir+"/"+fasta_file)
    mm_cmd = blast_bin+"/makemat -P "+seq_name
    print(mm_cmd)
    start_time = time.time()
    p = subprocess.Popen(shlex.split(mm_cmd), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.wait()

    end_time = time.time()
    runtime = math.ceil(end_time-start_time)
    try:
        shutil.copy(out_dir+"/"+seq_name+".mtx", out_dir+"/"+seq_name+".lmtx")
    except Exception as e:
        pass

    hit_count = get_num_alignments(out_dir+"/"+seq_name+".xml")
    pssm_data = get_pssm_data(out_dir+"/"+seq_name+".lmtx")
    request_data["file_data"] = pssm_data
    entry_data = {"name": seq_name, "file_type": 2, "md5": file_contents['md5'],
                  "blast_hit_count": hit_count, "runtime": runtime,
                  "sequence": file_contents['seq'],
                  "data": str(request_data).replace('"', '\\"').replace('\n', '\\n'),
                  }
    # print(entry_data['data'])
    r = requests.post(entry_uri, data=entry_data)
    print("Submission Response:", r.status_code)
else:
    # get blast file from cache
    print("Cache Response:", r.status_code, "retrieved file from cache")
    if r.status_code == 200:
        response_data = json.loads(r.text)
        if 'data' in response_data:
            response_data['data']['file_data'] = \
            response_data['data']['file_data'].replace('seq-data ncbistdaa "',
                                                       "seq-data ncbistdaa '")
            response_data['data']['file_data'] = \
            response_data['data']['file_data'].replace('"H\n',
                                                       "'H\n")
            f = open(seq_name+".lmtx", 'w')
            # before printing we should really
            # sanity check that data is a
            # psiblast pssm
            f.write(response_data['data']['file_data']+'\n')
            f.close
    else:
        # panic
        eprint("Blast cache request returned nether 404 or 200!!!")
        exit(1)
