# Web Search Engine 

All work for my web search engine project. 

0. **crawl.py** - pagerank, breadth first and breadth limited search implemeted on a crawled web graph

1. **parsedata.py** - read the common crawl dataset (WET format) and output temp index files for each input file and also create global pagetable file

2. **mergesort.sh** - sort temporary index on disk and merge to a globally sorted file on disk, chunked into files of 2M lines each

3. **makeindex.py** - read merged chunks and create final lexicon and index file

4. **queryprocess.py** - query processor run on generated index files (lexicon, pagetable, index)
