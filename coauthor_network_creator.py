#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 16:43:57 2019

@author: jorge
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 11:33:00 2018

@author: jorge
"""

import json
import sys
import itertools

venues = sys.argv[1]
seed_venues = venues.split("_")
seed_venues = [s.lower() for s in seed_venues] ##we have to check this with grep on the data file, in case of kdd the venue is written in lower

seed_ids = {}
seed_authors = {}


save_file = sys.argv[2]


##write venues full name to inside venues file
#inside_file = "/".join(pubs_file.split("/")[:-1]) + "/inside_venues.txt"
#fwrite = open(inside_file, "w")
#for v in seed_venues:
#    fwrite.write(v + "\n") 
#fwrite.close()
 

### get seeds documents
fwrite = open(save_file, "w")
with open("../data/dblp_12.2017.txt", "r") as fp:
    for line in fp:
        json_data = json.loads(line)
        pub_venue = json_data['venue'].lower()
        
        #############################################################################
        #                                                                           #
        # we are only considering collaborations within the venues is THIS CORRECT? #
        #                                                                           #
        #############################################################################
        
        if pub_venue in seed_venues: 
            #print pub_venue, "in", seed_venues
            authors = list()
            for a in json_data['authors']:
                a1 = a.encode('utf8')
                a1 = a1.replace('"', '')
                authors.append(a1)
            coauthorships = list(itertools.combinations(authors,2))
            year_collaboration = int(json_data['year'])
            for collab in coauthorships:
                fwrite.write('"%s","%s",%d\n' % (collab[0], collab[1],year_collaboration))

fwrite.close()

