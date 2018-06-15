# Read input - mergedchunks/*
# Output - final/invindex and final/lexicon
# Invindex format - list of bytes (compressed doc ids)
# Lexicon file format - {word : startoffset in invindex file, endoffset}
# Pagetable already created

import glob
import zlib
import struct

IIF = open('FINAL/invindex', 'ab')
#COUNTER = 0

# Append docs to binary file
def writeindex(docs):
    #global COUNTER
    for d in docs:
        b = struct.pack('i',int(d))
        IIF.write(b) #compress?
        #COUNTER += 1
        #if COUNTER > 5000:
        #    IIF.flush()

lexicon = {}
currentoffset = 0
currentword = None

for filename in glob.glob("mergedchunks_m/*"):
    f = open(filename,'r')
    print('Looking at', filename)
    for line in f:
        record = line.split('\t')
        word = record[0].strip()
        docs = record[1].split()
        writeindex(docs)

        if word != currentword:
            startoffset = currentoffset
            endoffset = startoffset + len(docs) - 1
        else:
            startoffset = lexicon[word][0]
            endoffset = lexicon[word][1] + len(docs)
            
        lexicon[word] = (startoffset, endoffset)
        currentoffset = endoffset + 1
        currentword = word

    f.close()

IIF.close()

print('Writing PT')
with open('FINAL/lexicon','w') as f:
    for i in lexicon:
        f.write(i)
        f.write('\t')
        f.write(str(lexicon[i][0]))
        f.write(' ')
        f.write(str(lexicon[i][1]))
        f.write('\n')


