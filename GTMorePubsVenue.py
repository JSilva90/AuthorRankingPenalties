#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 14:05:20 2019

@author: jorge
"""

import sys
import csv

data_file = sys.argv[1] ##file in format "author",year,"venue","pub_id"
min_year = int(sys.argv[2])
max_year = int(sys.argv[3])

#gt_file = sys.argv[4]

save_file = "/".join(data_file.split("/")[:-1]) + "/GT_mostpubs_%d_%d.csv" % (min_year, max_year)
write_file = open(save_file, "w")

with open(data_file, 'r') as csvfile: ##get all the publications after certain year from the file
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        [author, author_pos, n_authors, year, venue, pid] = row
        if int(year) >= min_year and int(year) < max_year:
            write_file.write('"%s","%s",1.0,%.4f,%.4f\n' % (author, pid, (1/float(n_authors)), (1/float(author_pos)) ))
write_file.close()
        
        
        
'''

authors_uni = dict() ##1 point per authorship
authors_div = dict() ## 1/point per authorship
authors_pos = dict() ## 1/n where n is the pos of the author in the paper        
        if int(year) >= min_award_year and int(year) < max_award_year:
            if author not in authors_uni:
                authors_uni[author] = 0.0
                authors_div[author] = 0.0
                authors_pos[author] = 0.0
            authors_uni[author] += 1
            authors_div[author] += 1 / (float(n_authors))
            authors_pos[author] += 1 / float(author_pos)
         
            
        
            
print "There are %d authors after year %d and before %d" % (len(authors_uni), min_award_year, max_award_year)


def sortDict(authors):
    authors = [(a, authors[a]) for a in authors]
    return sorted(authors, key=lambda tup: tup[1], reverse=True)

def writeAuthors(authors, gt_file):  
    f = open(gt_file, "w")
    for a in authors:
        f.write('"%s",%f\n' % (a[0], a[1]))
    f.close()
    
authors_uni = sortDict(authors_uni)
authors_div = sortDict(authors_div)
authors_pos = sortDict(authors_pos)

save_file = "/".join(data_file.split("/")[:-1]) + "/GT_mostpubs_%d_%d_%s.txt"

writeAuthors(authors_uni, save_file % (min_award_year, max_award_year, "uni"))
writeAuthors(authors_div, save_file % (min_award_year, max_award_year, "div"))
writeAuthors(authors_pos, save_file % (min_award_year, max_award_year, "pos"))
'''
