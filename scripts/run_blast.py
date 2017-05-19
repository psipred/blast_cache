import requests
import sys

# arg 1 input fasta file
# arg 2 output dir
# arg 3 base uri
# arg 4 blast bin path
# arg 6 blast settings string
# arg 5 blast db

#
# python run_blast.py ../files/P04591.fasta ../files http://127.0.0.1:8000 /scratch0/NOT_BACKED_UP/dbuchan/Applications/ncbi-blast-2.2.31+/bin/ /scratch1/NOT_BACKED_UP/dbuchan/uniref/uniref_test_db/uniref_test -num_alignments 0 -num_threads 2



fasta_file = sys.argv[1]  # path to input fasta
out_dir = sys.argv[2]  # path to place blast output and PSSM files
base_uri = sys.argv[3]  # ip or URI for the server blast_cache is running on
blast_bin = sys.argv[4]  # path to the blast binary dir
blast_db = sys.argv[5]  # path to blast db location
blast_settings = " ".join(sys.argv[6:]) # get everything else on the commanline
#                                         make it a string and use it as the
#                                         blast settings
seq_name = fasta_file.split("/")[-1].split(".")[0]
