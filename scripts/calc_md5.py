import hashlib
import sys


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


fasta_file = sys.argv[1]
file_contents = read_file(fasta_file)
print(file_contents['md5'])
