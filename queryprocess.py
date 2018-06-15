# coding: utf-8

import numpy as np
import struct
from collections import Counter

# Load pagetable
pagetable = {}
doclens = []
with open('FINAL/pagetable') as f:
    for line in f:
        docid, url, size = line.split()
        doclens.append(int(size))
        pagetable[int(docid)] = (url, int(size))

maxdocid = list(pagetable.keys())[-1]
davg = np.mean(doclens)
#len(pagetable)


# Load lexicon
lexicon = {}
with open('FINAL/lexicon','r') as f:
    for line in f:
        linedata = line.split()
        if len(linedata)==3:
            word, start, end = line.split()
            lexicon[word] = (int(start), int(end))
#len(lexicon)



f = open('FINAL/invindex','rb')

def openlist(t):
    return lexicon[t][0], lexicon[t][1]

def nextgeq(lp, endlp, k):
    start = 4*lp
    end = 4*endlp
    while(start <= end):
        f.seek(start)
        c = struct.unpack('i',f.read(4))[0]
        if c>=k:
            return c
        start += 4
    return 9999999

#lp, end = openlist('july')
#nextgeq(lp, end, 1)


def getfreq(lp, endlp, d):
    f = 0
    start = 4*lp
    end = 4*endlp
    while(start <= end):
        f.seek(start)
        doc = struct.unpack('i',f.read(4))[1]
        if doc==d:
            f += 1
        start += 4
    return f

# length of posting
def iilen(term):
    (start, end) = lexicon[term]
    return end-start+1

# score of query q wrt docid d
def bm25(q, d, freqs):
    N = len(pagetable)
    lend = pagetable[d][1]
    k1,b = 1.2, 0.75
    K = k1*((1-b) + b*lend/davg)
    
    score = 0
    for i in range(len(q)):
        ft = iilen(q[i])
        fdt = freqs[i]
        score += np.log( (N - ft + 0.5) / (ft + 0.5) ) * (k1 + 1) * fdt / (K + fdt)
    return score    


def printtopscores(d):
    if not d:
        print('No results')
        return 0
    d = dict(Counter(d).most_common(5))
    for i in d:
        print(pagetable[i][0], d[i])
    return 1


# main document at a time query processor
def daatqp(q):
    lps = []
    ends = []
    freqs = []
    did = 0
    allscores = {}

    for i in range(len(q)):
        try:
            op = openlist(q[i])
        except:
            return None
        lps.append(op[0])
        ends.append(op[1])
    
    while(did <= maxdocid):
        did = nextgeq(lps[0], ends[0], did)
        #print('did = ', did)
        d = 0
        for i in range(1, len(q)):
            d = nextgeq(lps[i], ends[i], did)
            #print('d = ', d)
            if d!=did:
                break
                
        if d>did:
            did = d
            
        elif did!=9999999:
            for i in range(len(q)):
                freqs.append(getfreq(lps[i], ends[i], d))
            #print(q, did)
            score = bm25(q, did, freqs)
            allscores[did] = score
            did += 1

    return allscores


#query = input()
query = 'cat dog'

# AND
allscores = daatqp(query.split())
returncode = printtopscores(allscores)
#if returncode!=0:
#    print(len(allscores))



# OR
allscores = {}
for q in query.split():
    allscores.update(daatqp([q]))
returncode = printtopscores(allscores)




