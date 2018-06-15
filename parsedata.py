# Read input - files/*.warc.wet.gz
# Output - index file for each input file (unsortedchunks/myfile#), pagetable file (final/pagetable)
# Index files format - unsorted {word : [docids]}
# Pagetable file format - {docid : url}
# Run and pass results to mergesort.sh


import warc
import sys
import glob
import re

#regex = re.compile(r'^[a-zA-Z]+$')

# Add docs from file to global PAGETABLE and words to local INVINDEX
def parsefile(filename):
    f = warc.WARCFile(filename, 'r')
    invindex = {}
    pagetablekey = 1 + len(PAGETABLE)
    for record in f:
        url = record.header.get('warc-target-uri', None)
        if not url:
            continue

        words = record.payload.read().split()
        PAGETABLE[pagetablekey]= (url, len(words))
        for w in set(words):
            #if regex.match(w.decode('utf8')):
            if w not in invindex:
                invindex[w] =  [pagetablekey]
            else:
                invindex[w].append(pagetablekey)
        pagetablekey += 1

    f.close()
    return invindex


def diskWritePT():
    print('Writing PT to ~pagetable~')
    with open("FINAL/pagetable", "w") as f:
        for i in PAGETABLE:
            f.write(str(i))
            f.write('\t')
            f.write(PAGETABLE[i][0])
            f.write(' ')
            f.write(str(PAGETABLE[i][1]))
            f.write('\n')


def diskWriteII(invindex, num):
    print('Writing II to ~myfile' + str(num) + '~')
    with open('unsortedchunks/myfile'+str(num), 'w') as f:
        for w in invindex:
            f.write(w.decode('utf8'))
            f.write('\t')
            for d in invindex[w]:
                f.write(str(d)+' ')
            f.write('\n')

PAGETABLE = {}
num = 0
#for filename in ['files/CC-MAIN-20170919112242-20170919132242-00000.warc.wet.gz']:
for filename in glob.glob("files/*.wet.gz"):
    num += 1
    invindex = parsefile(filename)
    diskWriteII(invindex, num)
    del invindex

diskWritePT()
del PAGETABLE


