#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 13:30:50 2019

@author: jorge
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 14:53:29 2019

@author: jorge
"""


import networkx as nx
import multiprocessing as mp
import csv
import sys
import random
import time
import matplotlib.pyplot as pl
import numpy as np
import math

results = list()
collabs = dict()

pen_type = ""


#decay_age = 5.0 #decay for age function e^(-(time_passed/decay_age))
#data_file = "teste.csv"



def createCitNetwork(citations):
    G = nx.MultiDiGraph()
    with open(citations, "r") as fp:
        csv_reader = csv.reader(fp, delimiter=',',quotechar='"')
        for line in csv_reader:
            try:
                [citing_author, cited_author, year, venue, weight, author_pos] = line
            except Exception as e:
                print (line)
                print (e)
                quit()
            G.add_edge(citing_author, cited_author, attr_dict={'year':int(year), 'venue':venue, 'weight':float(weight), 'author_position':author_pos})		
    return G



def createNetwork(data_file): ##reads the co_authorships file and create a networkx graph
    G = nx.MultiGraph()
    with open(data_file, "r") as fp:
        csv_reader = csv.reader(fp, delimiter=',',quotechar='"')
        for line in csv_reader:
            try:
                [author_1, author_2, year] = line
            except Exception as e:
                print (line)
                print (e)
                quit()
            G.add_edge(author_1, author_2, attr_dict={'year':int(year)})		
    return G



#dists = nx.shortest_path_length(G) ##this takes forever to run even for a one conference network, we need to make this more efficient!
##lets just have a dict of neighbours and then when estimating penalty we search the dict for neighbours of neighbours, we limit this to 3 hops for efficieny
def createCoAuthorDict(G):
    co_authors = dict()
    for a1 in G.nodes():
        co_authors[a1] = dict()
        for con in G.edges(nbunch=[a1], data = True):
            if con[1] not in co_authors[a1]:
                co_authors[a1][con[1]] = list() ##each neighbour as a number of coauthorships and a list with the years of the collaborations
            co_authors[a1][con[1]].append(int(con[2]['year']))
    return co_authors
                

            
def getValidPaths(author_collabs, year):
    """
    selects the neighbours with valid paths
    returns a list where each result is a tuple of author name, collaborations < year
    """
    valid_neighbours = list()
    for n in author_collabs:
        valid_collabs = list()
        for c in author_collabs[n]:
            if c < year:
                valid_collabs.append(c)
        if len(valid_collabs) > 0:
            valid_neighbours.append((n, list(valid_collabs)))
    return valid_neighbours

def estimatePenaltyWeight(previous_collabs, year, pen_type):
    """
    given a link it calculates the penalty based on a certain pen type
    """
    decay = 5.0
    pen = 1.0
    if "D" in pen_type:
        pen = 0.75 ## the direct penalty from 1 hop is always 0.75, if there are two hops then it will be 0.75 * 0.75
    if "A" in pen_type:
        most_recent_collab = max(previous_collabs)
        if most_recent_collab >= year:
            print ("collabs > than year aborting mission in penalty estimation")
            quit()
        pen *= (math.exp(-((year - most_recent_collab) / decay)))
    if "F" in pen_type:
        pen *= (1- (math.exp(-(len(previous_collabs) / decay))))
    return pen

def duplicatesRemoval(checked, node, path_penalty):
    """
    IF A collaborated with B, B is also connected to A so when checking B we do not need to add A
    however since we have multi path this is not as straightforward, we are only not required to add the node if we found a previous path to the node that presents an higher penalty than the new one.
    This function achieves that
    """
    if node not in checked:
        checked[node] = path_penalty
        return True
    if checked[node] < path_penalty:
        checked[node] = path_penalty
        return True
    else:
        return False


def findCollab(collabs, source, target, year, max_hop, pen_type):
    """
    """
    #print "Looking for path %s to %s" % (source, target) 
    if source == target: #3penalty for auto-citations is 100%
     #   print "returning 1.0"
        return 1.0
    if source not in collabs or target not in collabs:
      #  print "no connection returning 0.0"
        return 0.0  #either the source or the target do not have any collaborations 
    
    if len(collabs[source]) > len(collabs[target]): ##try to optmize by starting the search with the node with fewer neighbours
        aux = source
        source = target
        target = aux
        
    #nodes_to_check = [(0.0, 1, x) for x in collabs[source].keys()] ##add all the direct neighbours with current penalty 0.0 and at hop 1
    nodes_to_check = [(1.0, 0, source)]
    
    checked = {source : 1}
    #next_nodes = list()
    max_pen = 0.0 
    processed = 0
    
    while (len(nodes_to_check) > 0): ##while there are nodes to check
        if max_pen >= nodes_to_check[0][0]: #if the current max penalty awarded is higher than any current possible paths stop the search
            #print "broke out %f" % max_pen
            break
        node = nodes_to_check.pop(0)
        processed += 1
        #if random.randint(0,100) == 0:
            #print "From %s to %s, %f, %d, left: %d, max_pen: %f, processed: %d" % (source, node[2], node[0], node[1], len(nodes_to_check), max_pen, processed)
        for path in getValidPaths(collabs[node[2]], year): ##get valid neighbours, i.e the ones with collaborations before year
            link_penalty = estimatePenaltyWeight(path[1], year, pen_type) ##calculate the penalty for the link
            path_penalty = node[0] * link_penalty ## the all the wya penalty is a multiplication of the all the penalty links along the path
            if path[0] == target: ##if it is the target then update the max penalty
                if path_penalty > max_pen:
                    max_pen = path_penalty
            elif node[1] < (max_hop-1) and path_penalty > max_pen and duplicatesRemoval(checked, path[0], path_penalty): ##we only want to explore nodes where the max penalty may improve and we haven't passed the hop limit
                nodes_to_check.append((path_penalty, node[1] + 1, path[0]))
        nodes_to_check = sorted(nodes_to_check, key=lambda tup: tup[0], reverse=True)
    #print "%s to %s penalty is %f processed %d" % (source, target, max_pen, processed)
    return max_pen
            

        
            
def estimateEdgePenalty(edge, max_hop=3):
    global collabs
    global pen_type
      
    citing_author = edge[0]
    cited_author = edge[1]
    year = int(edge[2]['year'])
    edge[2]['co_author_penalty'] = findCollab(collabs, citing_author, cited_author, year, max_hop, pen_type)
    return edge

                    
if __name__ == '__main__':
    coauthor_file = sys.argv[1]
    cit_file = sys.argv[2]
    pen_type = sys.argv[3]
    pen_name = sys.argv[4]
    
    t1 = time.time()
    
    #global collabs
    g_collab = createNetwork(coauthor_file)
    collabs = createCoAuthorDict(g_collab)
    g_cit = createCitNetwork(cit_file)
    
    t2 = time.time()
    pool = mp.Pool(mp.cpu_count())
    #results = [estimateEdgePenalty(edge) for edge in g_cit.edges(data=True)]
    #results = pool.map_async(estimateEdgePenalty, [edge for edge in g_cit.edges(data=True)])
    results = pool.map(estimateEdgePenalty, [edge for edge in g_cit.edges(data=True)])
    #results = [pool.apply(estimateEdgePenalty, args=(edge, pen_type)) for edge in g_cit.edges(data=True)]
    
    pool.close()
    #pool.join()
    
    
    print ("took %f to load data" % (t2-t1))
    print ("took %f on complete process" % (time.time() - t1))
    #for e in g_cit.edges(data=True):
    #quit()
    new_file = cit_file.replace(".csv", "_" + pen_name + ".csv")
    save_file = open(new_file, "w")
    
    co_penalties = []
    
    for edge in results:
        save_file.write('"%s","%s",%d,"%s",%f,%d,%f\n' % (edge[0], edge[1], int(edge[2]['year']), edge[2]['venue'], edge[2]['weight'], int(edge[2]['author_position']), edge[2]['co_author_penalty']))
        co_penalties.append(edge[2]['co_author_penalty'])
    save_file.close()
    
    print ("Saved file %s" % new_file)
    """ 
    #this does not work on sibila  
    co_penalties = np.array(co_penalties)
    fig = pl.hist(co_penalties, normed=0)
    pl.title('Penalty histogram for network %s' % cit_file.replace(".csv",""))
    pl.xlabel("Penalty")
    pl.ylabel("Frequency")
    pl.savefig(cit_file.replace(".csv", "_" + pen_name + ".png"))
    
    print "plot saved at %s" % cit_file.replace(".csv", "_" + pen_name + ".png")
    #for e in results:
    #    if random.randint(0, 10) == 0:
    #        print e[2]['co_author_penalty']
            
    print "took %f to load data" % (t2-t1)
    print "took %f on complete process" % (time.time() - t1)
    """   
    ##createNHopCollabNetwork(collabs, g_cit)
    
        
        
        

