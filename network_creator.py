#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 11:33:00 2018

@author: jorge
"""

import json
import sys
import os

class Publication():
    def __init__(self, authors, ref_id, n_cit, year, venue):
        self.authors = authors
        self.ref_id = ref_id
        self.n_citations = n_cit
        self.year = year
        self.venue = venue.replace(',', '')
        
class Author():
    def __init__(self, name):
        self.name = name
        self.total_citations = 0
        self.year_citations = {}
        self.year_venues = {}
        self.publications_refs = [] ##if we need to get other information like number of authors or anything
        
    def addPublication(self, p_id, year, n_cit, venue):
        self.publications_refs.append(p_id)
        if year not in self.year_citations:
            self.year_citations[year] = []
        if year not in self.year_venues:
            self.year_venues[year] = []
        self.year_citations[year].append(n_cit)
        self.year_venues[year].append(venue)
        self.total_citations += n_cit
        

        
venues = sys.argv[1]
seed_venues = venues.split("_") ##multiple venues are separated with "_"
seed_venues = [s.lower() for s in seed_venues] ##we have to check this with grep on the data file, in case of kdd the venue is written in lower

seed_ids = {}
seed_authors = {}


save_file = sys.argv[2]
pubs_file = sys.argv[3] ##file name to save the ids of the publications used in the total network. Necessary to test the complete network
#print sys.argv
try:
    max_year = int(sys.argv[4]) ##filter the pubs up to a certain year. If year = 2016 only publications with year < than 2016 aer considered
except:
    print ("not considering year")
    max_year = 2999

##write venues full name to inside venues file
#inside_file = "/".join(pubs_file.split("/")[:-1]) + "/inside_venues.txt"
#fwrite = open(inside_file, "w")
#for v in seed_venues:
#    fwrite.write(v + "\n") 
#fwrite.close()
venue_counts = {v : 0 for v in seed_venues}

authors_file = "/".join(save_file.split("/")[:-1]) + "/venue_authors.txt"
write_authors = not os.path.exists(authors_file) #3if file already exists do not write it
 

### get seeds documents
with open("../data/dblp_12.2017.txt", "r") as fp:
    for line in fp:
        json_data = json.loads(line)
        pub_venue = json_data['venue'].lower()
        if pub_venue in seed_venues:
            #print pub_venue, "in", seed_venues
            venue_counts[pub_venue] += 1
            pub = Publication(json_data['authors'], json_data['id'], int(json_data['n_citation']), int(json_data['year']), json_data['venue'])
            seed_ids[json_data['id']] = pub
            author_pos = 0
            for a in json_data['authors']:
                if a not in seed_authors:
                    aux = Author(a)
                    seed_authors[a] = aux
                    ##write the author to the file, format: author, author_pos, number of authors, year, venue, pub_id, 
                seed_authors[a].addPublication(json_data['id'], int(json_data['year']), int(json_data['n_citation']), json_data['venue'])
                author_pos += 1
                if write_authors:
                    f = open(authors_file, "a")
                    a1 = a.encode('utf8')
                    a1 = a1.replace('"', '')
                    f.write('"%s", %d, %d, %d,"%s","%s"\n' % (a1, author_pos, len(json_data['authors']), int(json_data['year']), json_data['venue'].encode('utf8'), json_data['id'].encode('utf8')))
                    f.close()

#for v in venue_counts:
 #   print v + "," + str(venue_counts[v])
#MyUtils.saveObj(seed_authors, authors_info_save_file) ##save the seed info into a file
               
most_pub_authors = []
most_cited_authors = []    
for a in seed_authors:
    most_pub_authors.append((a, len(seed_authors[a].publications_refs)))
    most_cited_authors.append((a, seed_authors[a].total_citations))
    
most_pub_authors = sorted(most_pub_authors, key = lambda tup:tup[1], reverse=True)
most_cited_authors = sorted(most_cited_authors, key = lambda tup:tup[1], reverse=True)

pubs_refs = seed_ids.keys()

fwrite = open(save_file, "w")
with open("../data/dblp_12.2017.txt", "r") as fp:
    for line in fp:
        json_data = json.loads(line)
        pid = json_data['id']
        if 'references' not in json_data:
            continue
        refs = json_data['references']
        if int(json_data['year']) >= max_year:
            continue
        for ref in refs:
            if ref in seed_ids:
                if pid not in pubs_refs:
                    pubs_refs.append(pid)
                venue = json_data['venue'].encode('utf8')
                title = json_data['title'].encode('utf8')
                title = title.replace('"', '')
                #venue = re.sub('[\W_]+',' ', venue, flags=re.UNICODE)
                #title = re.sub('[\W_]+',' ', venue, flags=re.UNICODE)
                #venue = venue.replace(",", "")
                #title = title.replace(",", "")
                #title = title.replace('"', "")
                for citing_author in json_data['authors']:
                    author_pos = 1
                    a1 = citing_author.encode('utf8')
                    #a1 = re.sub('[\W_]+',' ', a1, flags=re.UNICODE)
                    
                    a1 = a1.replace('"', '')

                    for cited_author in seed_ids[ref].authors:
                        a2 = cited_author.encode('utf8')
                        #a2 = re.sub('[\W_]+',' ', a2, flags=re.UNICODE)
                        #
                        a2 = a2.replace('"',"")
                        #print '"%s","%s",%d,"%s","%s",%.3f,%d' % (a1, a2, json_data['year'], venue, title, 1/float(len(seed_ids[ref].authors)), author_pos)
                        fwrite.write('"%s","%s",%d,"%s",%.3f,%d\n' % (a1, a2, json_data['year'], venue, 1/float(len(seed_ids[ref].authors)), author_pos))
                        #print '"%s","%s",%d,"%s",%.3f,%d' % (a1, a2, json_data['year'], venue, 1/float(len(seed_ids[ref].authors)), author_pos) 
                        author_pos += 1
fwrite.close()
                        
              
fwrite = open(pubs_file, "w")
for p_id in pubs_refs:
    fwrite.write('"%s"\n' % p_id)
fwrite.close()






    
    


