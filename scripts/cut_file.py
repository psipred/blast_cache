# 625
# 954
# 1377
# 1686

boundaries = [[0, 625], [625, 954], [954, 1377], [1377, 1686]]

with open("../files/all.fasta", "rb") as fastafile:
    for bound in boundaries:
        fastafile.seek(bound[0])
        bytelength = bound[1] - bound[0]
        data = fastafile.read(bytelength)
        line = data.decode("utf-8")
        print(line)
