# Breadth first exploration of links
# Queue initialized to initiallinks
# Make graph    
# Calculate PR on graph every step
# Dequeue max PR from queue and visit or dequeue like regular BFS (set toggle to choose)
# Keep track of explored
# Limit by number of pages visited
# Handle leaks and sinks in PR
# Save visited pages, size, estimated PR, PR at end
# Url parsing (urlparse, urljoin), normalization
# Handle non html pages, cgi scripts
# Robot exclusion
# Set parameter to limit pages per site 

import requests
from bs4 import BeautifulSoup
import re
import queue
import copy
import numpy as np
import pandas as pd
import urllib.parse
import robotexclusionrulesparser
from scipy.sparse import csc_matrix

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

#robots.txt parsing. True if allowed
def access_right(currentURL):
    try:
        rerp = robotexclusionrulesparser.RobotExclusionRulesParser()
        robotpath = find_base(currentURL) + '/robots.txt'
        rerp.fetch(robotpath)
        return rerp.is_allowed("*", currentURL)
    except:
        return True

#Get base URL
def find_base(url):
    proto, rest = urllib.parse.splittype(url)
    host, rest = urllib.parse.splithost(rest)
    return 'http://' + host

#Parse url
def urlclean(url):
    #can do other parsing
    return urllib.parse.urlsplit(url).geturl()


search = input()

#Initialize top google searches
initiallinks = []
page = requests.get("https://www.google.com/search?q={}".format(search))
soup = BeautifulSoup(page.content, "html5lib")
links = soup.findAll("a")
for link in links :
    href = link.get('href')
    if "url?q=" in href and not "webcache" in href:
        l = link.get('href').split("?q=")[1].split("&sa=U")[0]
        initiallinks.append(urlclean(l))

initiallinks = set(initiallinks)        


#Get all links in give url
def getalllinks(url):
    alllinks = []
    if not access_right(url):
        return
    try:
        r = requests.get(url, headers=headers, timeout=1)
        print(r.status_code, pd.datetime.now())
    except:
        return
    '''with open('results','a') as f:
        f.write(url + ' ' + depth + ' ' + r.status_code + ' ' + pd.datetimenow() + '\n')
    with open('pages','a') as f:
        f.write(url+'\n' +str(r.content)+'\n\n')'''

    soup = BeautifulSoup(r.content, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.startswith('http'):
            alllinks.append(urlclean(href))
        if len(alllinks)==25:
            break
    return alllinks

#Basic BFS limited by number of explored pages

LIMIT = 500
def bfs(initiallinks):
    no = 0
    depth = 1
    q = queue.PriorityQueue()
    for i in initiallinks:
        q.put((depth, i))
    explored = set()
    
    while q.qsize() and len(explored) < LIMIT:
        currentdepth, current = q.get()
        if current not in explored:
            explored.add(current)
            no += 1
            print(no, current, currentdepth)
            for neighbor in getalllinks(current) or []:
                if neighbor not in explored:
                    q.put((currentdepth + 1, neighbor))        
    
bfs(initiallinks)

#Pagerank implemented on adjacency matrix. Not original code
def pageRank(A,n, s=0.85):
    #print('calculating pagerank on size ', n)
    rsums = np.array(A.sum(1))[:,0]
    ri, ci = A.nonzero()
    A.data /= rsums[ri]
    sink = rsums==0

    ro, r = np.zeros(n), np.ones(n)
    iterations = 0
    while np.sum(np.abs(r-ro))>0.1:
        iterations += 1
        if iterations>30:
            break
        ro = r.copy()
        for i in range(n):
            Ai = np.array(A[:,i].todense())[:,0]
            Di = sink / n
            Ei = np.ones(n) / n
            r[i] = np.dot(ro, Ai*s + Di*s + Ei*(1-s))
    return 1 - r/sum(r)

#M2 = np.array([[0] * 100 for i in range(100)])
#pageRank(M1)


class Graph:
    def __init__(self, x):
        self.list = {}
        self.nodes = []
        for i in x:
            self.list[i] = set()
        self.nodes = self.list.keys()

    def addEdge(self, fromnode, tonode):
        if tonode not in self.list:
            self.list[tonode] = set()
        if fromnode in self.list:
            self.list[fromnode].add(tonode)
        else:
            self.list[fromnode] = set(tonode)
        self.nodes = self.list.keys()

    def getMatrix(self):
        M = [[0] * len(self.nodes) for i in range(len(self.nodes))]
        for i in self.list:
            rowind = list(self.list).index(i)
            for j in self.list[i]:
                colind = list(self.list).index(j)
                M[rowind][colind] = 1
        return np.array(M), list(self.list.keys())


#BFS by pagerank values
LIMIT = 5
def prbfs(initiallinks):
    no = 0
    G = Graph(initiallinks)
    adjM, nodes = G.getMatrix()
    #pagerank = pageRank(adjM)
    pagerank = pageRank(csc_matrix(adjM, dtype=np.float), adjM.shape[0])
    q = queue.PriorityQueue()
    for i in range(len(nodes)):
        q.put((pagerank[i], nodes[i]))

    explored = set()
    while len(explored) < LIMIT:
        currentpr, current = q.get()
        if current not in explored:
            no += 1
            print(no, current, currentpr)
            explored.add(current)
            neighbors = getalllinks(current)
            if not neighbors:
                continue
            for neighbor in neighbors:
                if len(G.list)<300:
                    G.addEdge(current, neighbor)
            #print('Added ', len(neighbors), ' edges')
            adjM, nodes = G.getMatrix()
            #print('Calculated adjM.', len(nodes), ' nodes')
            #pagerank = pageRank(adjM)
            pagerank = pageRank(csc_matrix(adjM, dtype=np.float), adjM.shape[0])
            newq = queue.PriorityQueue()
            for i in range(len(nodes)):
                newq.put((pagerank[i], nodes[i]))
            q = newq

prbfs(initiallinks)
