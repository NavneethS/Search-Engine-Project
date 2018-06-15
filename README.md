# Web Search Engine 

All work for my web search engine project. 

0. crawl.py - pagerank, breadth first and breadth limited search on web graph after crawling

1. parsedata.py - read WET crawl data and output temp index files for each input file and global pagetable file

2. mergesort.sh - sort temporary index to on disk and merge to single file on disk chunked into size 2M lines each

3. makeindex.py - read merged chunks and create final lexicon and index file

4. queryprocess.py - query processor run on generated index files (lexicon, pagetable, index)
