#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 11:06:58 2018

@author: jorge
"""

from lxml import html
import sys
import re

html_file = "../data/best_papers.html"

f = open(html_file, "r")
html_string = f.read()
f.close()

tree = html.fromstring(html_string)
table = tree.cssselect('Table')
papers_table = table[0]

x = []
if sys.argv[1] == "all":
    confs_to_add = []
else:
    confs_to_add = sys.argv[1].split("_")
    
folder = sys.argv[2]
min_year = int(sys.argv[3])
max_year = int(sys.argv[4])

save_file = folder + "/awarded_authors_from_%d_to_%d.csv" % (min_year, max_year)

    
year = -1
write_file = open(save_file, "w")
for t in papers_table: ##the table consists of a set of thead and tbodies
    if t.tag == "thead":
        conference = t[0][0][0].text        
    else: ##if its not a thead its a tbody and we have to iterate through it
        gather = True
        if len(confs_to_add) > 0:
            gather = False
            for c in confs_to_add:
                if c.lower() == conference.split(" (")[0].lower():
                    gather = True
                    break
        if not gather:
            continue
        for tr in t:
            offset = 1
            try:
                year = int(tr[0][0].text)
            except:
                offset = 0
            authors = []
            if year < min_year or year >= max_year:
                continue
            title = tr[offset][0].text.encode('utf8')
            first_author = tr[offset+1].text.encode('utf8')
            first_author, inst = first_author.split(", ")
            author_pos = 1

            if "&" in first_author: ##handle cases where more than one author appears
                first_author, second_author = first_author.split(" & ")
                authors.append((first_author, inst, author_pos))
                author_pos += 1
                authors.append((second_author, inst, author_pos))
                author_pos += 1
            else:
                authors.append((first_author, inst, author_pos))
                author_pos += 1
                try:
                    if len(tr[offset+1]) > 1:
                        authors_info = html.tostring(tr[offset+1][1]).encode('utf8')
                        authors_info = authors_info.split('block;">')[1]
                        authors_info = authors_info.split('</div>')[0]
                    else:
                        authors_info = html.tostring(tr[offset+1][0]).encode('utf8')
                    other_authors = authors_info.split("<br>")
                        
                    for a in other_authors:
                        if a == "":
                            continue
                        name, inst = a.split(", ")
                        authors.append((name, inst, author_pos))
                        author_pos += 1
                except Exception as e:
                    ##usually happens when ther's only a single author in the publication still the author is recorded on the file
                    #print e
                    #print "Error getting other authors on %s" % title
                    pass
            #add_points = False
            #if ".." in title:
            #    add_points = True
            #title = re.sub('[\W_]+',' ', title, flags=re.UNICODE)
            #if add_points:
            #    title += "..."
            #title = title.decode("utf8", errors='ignore')
            #conference = conference.decode("utf8", errors='ignore')
            for a in authors:
                #author = re.sub('[\W_]+', ' ', a[0], flags=re.UNICODE)
                #author = author.decode('utf8', errors='ignore')
                #write_file.write('"%s","%s","%s",%.4f,%d\n' % (conference, a[0], title.lower(), (1/float(len(authors))), year))
                write_file.write('"%s","%s",1.0,%.4f,%.4f\n' % (a[0], title.lower(), (1/float(len(authors))),(1/float(a[2])) ))
                #print '"%s","%s","%s",%.4f' % (conference, author, title, (1/float(len(authors))))
                #print '"%s","%s","%s",%.4f' % (conference, a[0], title, (1/float(a[2])))
                
                #continue
                #print  '"%s","%s","%s",1.0' % (conference, a[0], title)
                #print '"%s",%d,"%s","%s","%s",%d,%d' % (conference, year, title, a[0], a[1], a[2], len(authors))
write_file.close()   

