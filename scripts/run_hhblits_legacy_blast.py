import requests
import sys
import hashlib
import subprocess
import shlex
import shutil
import os.path
import os
from Bio.Blast import NCBIXML
import time
import math
import json
import re
# arg 1 input fasta file
# arg 2 output dir
# arg 3 base uri
# arg 4 blast bin path
# arg 6 blast settings string
# arg 5 blast db
# arg 6 hhblits root/hh suite dir
# arg 7 hhblits db

#
# MUST SET HHLIB to match the HH-suite version see line 108
# USEAGE
# python scripts/run_hhblits_legacy_blast.py ./files/P04591.fasta ./files http://127.0.0.1:8000 /opt/Applications/blast-2.2.26/bin/ mtx /opt/Applications/hh-suite-3/ /scratch1/NOT_BACKED_UP/dbuchan/hhblitsdb/uniclust30_2017_10/uniclust30_2017_10 -a 12 -b 0 -j 2 -h 0.01

# python scripts/run_hhblits_legacy_blast.py ./files/P04591.fasta ~/tmp_cache http://128.16.14.80 /opt/blast-2.2.26/bin/ mtx /opt/hh-suite/ /data/hhdb/uniclust30_2018_08/uniclust30_2018_08 NULL -a 12 -b 0 -j 2 -h 0.01
# python scripts/run_hhblits_legacy_blast.py ./files/P04591.fasta ~/tmp_cache http://128.16.14.80 /opt/blast-2.2.26/bin/ mtx6 /opt/hh-suite/ /data/hhdb/uniclust30_2018_08/uniclust30_2018_08 ./files/P04691.a3m -a 12 -b 0 -j 2 -h 0.01 -F F


def read_file(path):
    with open(path, 'r') as myfile:
        data = myfile.read()
    seq_count = 0
    seqs = {0: ''}
    for line in data.split("\n"):
        if line.startswith(">"):
            seq_count += 1
            seqs[seq_count] = ''
        else:
            seqs[seq_count] += line.rstrip()
    m = hashlib.md5()
    if seq_count == 0:
        test_hash = m.update(seqs[0].encode('utf-8'))
        return({'seq': seqs[0], 'md5': m.hexdigest(), 'single': None})
    else:
        all_seqs = ''
        for seq in seqs:
            all_seqs += seqs[seq]
        test_hash = m.update(all_seqs.encode('utf-8'))
        return({'seq': all_seqs, 'md5': m.hexdigest(), 'single': seqs[1]})


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
    if os.path.isfile(path):
        with open(path) as myfile:
            pssm_data = myfile.read()
    else:
        eprint("Couldn't get PSSM data")
        exit(1)  # panic

    return(pssm_data)


def run_exe(args, name):
    """
        Function takes a list of command line args and executes the subprocess.
        Sensibly tries to catch some errors too!
    """
    code = 0
    print("Running "+name)
    try:
        print(' '.join(args))
        code = subprocess.call(' '.join(args), shell=True)
    except Exception as e:
        print(str(e))
        sys.exit(1)
    if code != 0:
        print(name+" Non Zero Exit status: "+str(code))
        sys.exit(code)


def make_flat_fasta_db(file, path):
    # read in a3m, output to temp file with no - or lowercase in seq
    flat_file = open(path+".flat",'w')
    if my_file.is_file(file):
        with open(file, 'r') as a3mfile:
            for line in a3mfile:
                if line.startswith('>'):
                    flat_file.write(line)
                else:
                    output_line = line.upper()
                    output_line = output_line.replace('-', '')
                    flat_file.write(output_line)
    flat_file.close()


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


fasta_file = sys.argv[1]  # path to input fasta
out_dir = sys.argv[2]  # path to place blast output and PSSM files
base_uri = sys.argv[3]  # ip or URI for the server blast_cache is running on
blast_bin = sys.argv[4]  # path to the blast binary dir
output_type = sys.argv[5]  # file endsing for PSSM file
hhblits_root = sys.argv[6]  # location of the hhblist bin
hhblits_db = sys.argv[7]  # location of the hhblist_db
a3m_alignment = sys.argv[8]
blast_settings = " ".join(sys.argv[9:])  # get everything else on the
#                                          commandline make it a string and
#                                          use it as the blast settings

# strings and data structures we need
seq_name = fasta_file.split("/")[-1].split(".")[0]
file_contents = read_file(fasta_file)
blast_input = fasta_file
sn_name = seq_name+".fasta"
if file_contents['single']:
    single_out = open(out_dir+"/"+seq_name+".sing", 'w')
    single_out.write(">single\n")
    single_out.write(file_contents['single'])
    single_out.close()
    blast_input = out_dir+"/"+seq_name+".sing"
    sn_name = seq_name+".sing"

entry_uri = base_uri+"/blast_cache/entry/"
entry_query = entry_uri+file_contents['md5']
i = iter(blast_settings.split())
request_data = dict(zip(i, i))

os.environ['HHLIB'] = hhblits_root

r = requests.get(entry_query, params=request_data)
print("Sending md5: " + file_contents['md5'])
print("Cache Response:", r.status_code)
print("Cache Response:", r.text)
hhblits_cmd = ''
reformat_cmd = ''
formatdb_cmd = ''
blast_cmd = ''
output_ending = ".a3m"
iterations = "3"
if output_type == 'mtx6':
    output_ending = ".a3m6"
    iterations = "1"

if r.status_code == 404 and "No Record Available" in r.text:

    hhblist_cmd = hhblits_root+"/bin/hhblits -d "+hhblits_db+" -i " + \
                  fasta_file+" -oa3m " + \
                  out_dir+"/"+seq_name+output_ending + \
                  " -e 0.001 -n "+iterations+" -cpu 2 " + \
                  "-diff inf -cov 10 -Z 100000 -B 100000 -maxfilt 100000 " + \
                  "-maxmem 5"
    reformat_cmd = hhblits_root+"/scripts/reformat.pl a3m psi " + \
        out_dir+"/"+seq_name+output_ending+" "+out_dir+"/"+seq_name+".psi"
    formatdb_cmd = blast_bin+"/formatdb -i " + \
        out_dir+"/"+seq_name+".flat " + \
        "-t "+out_dir+"/"+seq_name+".flat"
    blast_cmd = blast_bin+"blastpgp -d "+out_dir+"/" + \
        seq_name+".flat -i " + \
        blast_input+" -B "+out_dir+"/"+seq_name+".psi -C " + \
        out_dir+"/"+seq_name+".chk -a 2 "+blast_settings+" -m 7 -o " + \
        out_dir+"/"+seq_name+".xml "

    if output_type == 'mtx6':  # if this ending then we are restarting from an earlier mtx
        hhblist_cmd = hhblits_root+"/bin/hhblits -d "+hhblits_db+" -i " + \
                  a3m_alignment+" -oa3m " + \
                  out_dir+"/"+seq_name+output_ending + \
                  " -e 0.001 -n "+iterations+" -cpu 2 " + \
                  "-diff inf -cov 10 -Z 100000 -B 100000 -maxfilt 100000 " + \
                  "-maxmem 5"

    start_time = time.time()
    print("Running hhblits")
    print(hhblist_cmd)
    p = subprocess.Popen(shlex.split(hhblist_cmd), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.communicate()
    os.remove(out_dir+"/"+seq_name+".hhr")

    print("Running reformat")
    print(reformat_cmd)
    p = subprocess.Popen(shlex.split(reformat_cmd), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.communicate()

    make_flat_fasta_db(out_dir+"/"+seq_name+output_ending, out_dir+"/"+seq_name)

    print("Running formatdb")
    print(formatdb_cmd)
    p = subprocess.Popen(shlex.split(formatdb_cmd), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.communicate()

    print("Running blast")
    print(blast_cmd)
    p = subprocess.Popen(shlex.split(blast_cmd), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    res = p.communicate()
    print("stderr =", res[1])

    pn_cmd = "echo "+seq_name+".chk > "+out_dir+"/"+seq_name+".pn"
    sn_cmd = "echo "+sn_name+" > "+out_dir+"/"+seq_name+".sn"
    makemat_cmd = blast_bin+"makemat -P "+out_dir+"/"+seq_name
    os.system(pn_cmd)
    os.system(sn_cmd)
    try:
        shutil.copy(fasta_file, out_dir)
    except Exception as e:
        pass
    print("Running blast")
    print(pn_cmd)
    print(sn_cmd)
    print(makemat_cmd)
    os.chdir(out_dir)
    p = subprocess.Popen(shlex.split(makemat_cmd), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    res = p.communicate()
    print("stderr =", res[1])

    end_time = time.time()
    if output_type == 'mtx6':
        shutil.copy(out_dir+"/"+seq_name+".mtx", out_dir+"/"+seq_name+"."+output_type)
    os.chmod(out_dir+"/"+seq_name+"."+output_type, 0o666)
    # exit()
    runtime = math.ceil(end_time-start_time)
    hit_count = get_num_alignments(out_dir+"/"+seq_name+".xml")
    pssm_data = get_pssm_data(out_dir+"/"+seq_name+".mtx")
    request_data["file_data"] = pssm_data
    entry_data = {"name": seq_name, "file_type": 2,
                  "md5": file_contents['md5'],
                  "blast_hit_count": hit_count, "runtime": runtime,
                  "sequence": file_contents['seq'],
                  "data": str(request_data).replace('"', '\\"').replace('\n', '\\n'),
                  }
    r = requests.post(entry_uri, data=entry_data)
    print("Submission Response:", r.status_code)
    print("Response: ", r.text)
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
            f = open(seq_name+"."+output_type, 'w')
            # before printing we should really
            # sanity check that data is a
            # psiblast pssm
            f.write(response_data['data']['file_data']+'\n')
            f.close
            os.chmod(seq_name+"."+output_type, 0o666)

            dummy_cmd = "touch "+seq_name+output_ending
            os.system(dummy_cmd)

    else:
        # panic
        eprint("Blast cache request returned nether 404 or 200!!!")
        exit(1)
