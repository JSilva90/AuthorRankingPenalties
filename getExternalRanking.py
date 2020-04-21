#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 13:31:36 2018

@author: jorge
"""

import csv
import numpy as np
import json
import sys

class EqualGroup:
    def __init__(self, vals):
        self.values = vals
        self.min = min(vals)
        self.max = max(vals)
        self.avg = np.average(vals)
        
    def printGroup(self):
        print ("Group min %.2f, avg %.2f, max %.2f with %d elements" % (self.min, self.avg, self.max, len(self.values)))

class OutsideAuthor:
    def __init__(self, n):
        self.name = n.replace(",", "")
        self.total_citations = 0
        self.total_pubs = 0
        self.average_citation = -1
        self.min_group_val = 0
        self.max_group_val = 0
        self.avg_group_val = 0
        
    def addInfo(self, n_cit, n_pubs):
        self.total_citations = n_cit
        self.total_pubs = n_pubs
        if self.total_pubs > 0:
            self.average_citation = self.total_citations / float(self.total_pubs)
        else:
            self.average_citation = 0
        
    def updateGroupsInfo(self, groups):
        if self.average_citation < 0: ##if it doesn't exist add the smallest group val
            self.min_group_val = groups[0].min
            self.max_group_val = groups[0].max
            self.avg_group_val = groups[0].avg
            return
        for g in groups:
            if self.average_citation >= g.min and self.average_citation <= g.max:
                self.min_group_val = g.min
                self.max_group_val = g.max
                self.avg_group_val = g.avg
                break
                
    def printAuthor(self):
        return '"%s",%.3f,%.3f,%.3f' % (self.name, self.min_group_val, self.avg_group_val, self.max_group_val)

def getExternalAuthors(filename):
    """
    Returns the external authors of the network. The first column minus the ones that appear on the second column
    """
    inside_authors = {}
    outside_authors = {}
    with open(filename, "r") as fp:
        reader = csv.reader(fp, delimiter=',')
        for line in reader:
            try:
                [citing_author, cited_author, _, _, _, _] = line
            except:
                print ("Error reading the files")
                print (line)
                quit()
            if cited_author not in inside_authors:
                inside_authors[cited_author] = 1
            if citing_author not in outside_authors:
                outside_authors[citing_author] = 1
    exclusive_outside_authors = {}
    for n in outside_authors:
        if n not in inside_authors:
            aux = OutsideAuthor(n)
            exclusive_outside_authors[n] = aux
            
    return exclusive_outside_authors

def getAuthorsData(outside_authors, filename, max_year):
    """
    for the outside ones iterates through the authors information file and returns the number of citations and number of pubs
    """
    with open(filename, "r") as fp:
        for line in fp:
            data = json.loads(line)
            name = data['name'].encode('utf8')
            if name in outside_authors:
                #if 'paper_cits_by_year' not in data:
                #    quit()
                pub_years = [int(x) for x in data['npubs_by_year'].keys()]
                cit_years = [int(x) for x in data['paper_cits_by_year'].keys()]
                
                ##how to deal with outsiders that do not have any citaion / publication before the max year? at this stage we will just ignore them
                try:
                    p_year = max([x for x in pub_years if x < max_year])
                    c_year = max([x for x in cit_years if x < max_year])
                    outside_authors[name].addInfo(int(data['paper_cits_by_year'][str(c_year)]), int(data['npubs_by_year'][str(p_year)]))
                except:
                    continue
                    #outside_authors[name].addInfo(0,0)
                    #print name, " ", data['paper_cits_by_year'], max_year, data['npubs_by_year']



def equal_sum_groups(values, k):
    """
    I do not really want the equal sum because that would mean in order to have the exact sum, having low ranked authors to the best group just to round up the sum value
    So I'm adapting the algorithm, sorting the values, and adding values to the same group until the total sum of the group is sum(values) / k
    """
    aux_values = values
    aux_values.sort()
    sum_per_group = sum(values) / k
    groups_k = []
    groups_info = []
    offset = 0
    ##define min, max and average of each group
    for i in range(0,k):    
        groups_k.append(list())
        j = offset
        while j < len(aux_values) and sum(groups_k[i]) < sum_per_group:
            groups_k[i].append(aux_values[j])
            j += 1
        offset = j
        aux = EqualGroup(groups_k[i])
        groups_info.append(aux)
    return groups_info

"""
authors_file = "data/author_info.json"
network_file = "data/aaai/network.csv"
k_groups = 5
"""

network_file = sys.argv[1] #network
authors_file = sys.argv[2] ##authors json, this file contains global information for authors (such as total number of received citations, used to calculate external score for OTARIOS)
max_year = sys.argv[3] ##max citation year for the outsiders info
k_groups = int(sys.argv[4]) #3number of equal groups
save_file = sys.argv[5]
outside_authors = getExternalAuthors(network_file)
getAuthorsData(outside_authors, authors_file, max_year)
                
values = []
for name in outside_authors:
    author = outside_authors[name]
    if author.average_citation >= 0.0:
        values.append(author.average_citation)
        
groups = equal_sum_groups(values, k_groups)

#for g in groups:
#    g.printGroup()

write_file = open(save_file, "w")
for name in outside_authors:
    author = outside_authors[name]
    author.updateGroupsInfo(groups)
    aux = author.printAuthor()
    write_file.write(aux + "\n")
write_file.close()
    
    
    