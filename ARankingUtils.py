#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 16:01:32 2019

@author: jorge
"""
import re
import networkx as nx
import json
import csv
import os
import VenuesReader
###############################################
## Util functions
###############################################
        
        
def getPublicationsInfo(Venues, inside_venues, dblp_file, best_papers, i_best_papers, max_data_year):
    """
    Iterates throught the dblp file to save information for each node in the network. Each author should have a list of lists, 
    where each inner list consists of [n_authors, venue score, year] for each publication
    """
    regex = re.compile('[^a-zA-Z ]')
    matched_best_pubs = dict()
    max_pub_year = 0
    authors_info = dict()
    with open(dblp_file, "r") as fp:
        for line in fp:
            data = json.loads(line)
            if 'venue' in data and 'authors' in data and data['venue'].lower() in inside_venues: ##inside venue
                try:
                    year = int(data['year']) ## in case the year is not on the data
                    if year >= max_data_year:
                        continue
                    if year > max_pub_year: ##update max year for age probability calculation
                        max_pub_year = year
                except:
                    print "Publication without a year need to fix this..."
                    quit()
                n_authors = float(len(data['authors']))
                venue_score = getVenueScore(Venues, data['venue'].lower(), year)
                award_pub = False
                #title = encodeTitle(data['title'])
                title = data['title'].encode('utf8')
                title = regex.sub('',title)
                title = title.lower()
                if title in best_papers:
                    matched_best_pubs[title] = list()
                    best_papers.pop(title, None)
                    award_pub = True
                else:
                    for i in i_best_papers: ##some publications have incomplete names, try to match any title with the incomplete name
                        if i in title:
                            matched_best_pubs[title] = list()
                            i_best_papers.pop(i, None)
                            award_pub = True
                            break
                for author in data['authors']:
                    author = author.encode('utf8')
                    #author = encodeAuthorName(author)
                    if award_pub:
                        matched_best_pubs[title].append(author)
                    if author not in authors_info:
                        authors_info[author] = []
                    authors_info[author].append([n_authors, venue_score, year])                    
    print "Matched %d inside authors from dblp for venues: %s" % (len(authors_info), ";".join(inside_venues))
    return matched_best_pubs, authors_info,  max_pub_year
    
    
def getAuthorsGroundTruth(file):
    #authors_ground_truth = dict()
    regex = re.compile('[^a-zA-Z ]')
    best_papers = dict()
    incomplete_best_papers = dict() ##papers that are written with ... on title
    with open(file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            #[conference, author, paper, score, year] = row
            [author, paper, uni, equal, pos] = row
            incomp = False
            if "..." in paper: ##in order to know which titles are incomplete
                incomp = True
            paper = regex.sub('',paper)
            
            
            if incomp:
                if paper not in incomplete_best_papers:
                    incomplete_best_papers[paper] = list()
                incomplete_best_papers[paper].append(author)
            else:
                if paper not in best_papers:
                    best_papers[paper] = list()
                best_papers[paper].append(author)
    return best_papers, incomplete_best_papers


def getInsideVenues(folder):
    insidevenues_list = folder + "inside_venues.txt"
    inside_venues = set()
    with open(insidevenues_list, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            [venue] = row
            inside_venues.add(venue)
    return inside_venues

def removeGhosts(G, authors_info):
    n_to_remove = []  
    for n in G.nodes():
        if n not in authors_info:
            n_to_remove.append(n)
    print "Removed %d out of %d nodes from graph , because no author info" % (len(n_to_remove), G.number_of_nodes())
    for n in n_to_remove:
        G.remove_node(n)

def getInsideOutsideGraphs(G, inside_authors):
    
  
    Outside_G = G.copy()
    Inside_G = nx.empty_graph(0, create_using=nx.MultiDiGraph())
    
    
    for edge in G.edges(data=True, keys=True):
        citing_author = edge[0]
        
        if citing_author in inside_authors: ##the inside authors considers every author in the inside network
            year = edge[3]['year']
            author_position = edge[3]['author_position']
            venue = edge[3]['venue']
            weight = edge[3]['weight']
            venue_score = edge[3]['venue_score']
            coauthor_penalty = edge[3]['co_author_penalty']
            key = edge[2]
            
            Outside_G.remove_edge(edge[0], edge[1], key=key)
            Inside_G.add_edge(edge[0], edge[1], year=year, venue=venue, weight=weight, author_position=author_position, venue_score=venue_score, co_author_penalty=coauthor_penalty)
    
#    not_cited_authors = set()
#    for author in inside_authors: ##for nodes that are not cited and neither cite anybody
#        if author not in Inside_G.nodes():
#            Inside_G.add_node(author)
#            not_cited_authors.add(author)
    
    G.clear()
    return Inside_G, Outside_G#, not_cited_authors
	
def getVenueScore(venue_scores, venue, year):
	   venue = venue.replace(",", "")
	   venue = venue.lower()
	   venue_score = venue_scores.getVenueScoreYear(venue, year)
	   if not venue_score:
		   venue_score = venue_scores.getVenueScoreYear(venue, venue_scores.missing_year) ##if there's no value lets get the value from the missing year, i.e. the average of the other years
	   if not venue_score:
		   return venue_scores.epsilon ##if there's nothing for the venue return the epsilon
	   return venue_score	
	
def createNetwork(Venues, citations, n_pens, uniform_weight, allow_self_citations):
    G = nx.MultiDiGraph()
    with open(citations, "r") as fp:
        csv_reader = csv.reader(fp, delimiter=',',quotechar='"')
        for line in csv_reader:
            try:
                if n_pens == 0: #no_penalties associated to the file
                    [citing_author, cited_author, year, venue, weight, author_pos] = line
                elif n_pens == 1: ##one penalty associated to the file
                    [citing_author, cited_author, year, venue, weight, author_pos, pen1] = line
                else: ##in case that we have 2 penalties
                    [citing_author, cited_author, year, venue, weight, author_pos, pen1, pen2] = line
            except Exception as e:
                print line
                print e
                quit()
            venue_score = getVenueScore(Venues, venue, int(year))
            if not allow_self_citations and citing_author == cited_author:
                continue
                ##for the baseline we want to allow auto-citations. On the penalty networks this will be punished with 1.0 pen so they won't count. Still the score is split differently among the authors than it would be if we just ignore the link
            #    continue
            if uniform_weight:
                weight = 1.0
            if n_pens == 0:
                G.add_edge(citing_author, cited_author, attr_dict={'year':int(year), 'venue':venue, 'weight':float(weight), 'author_position':int(author_pos), 'venue_score': venue_score})
            elif n_pens == 1:
                G.add_edge(citing_author, cited_author, attr_dict={'year':int(year), 'venue':venue, 'weight':float(weight), 'author_position':int(author_pos), 'venue_score': venue_score, 'pen1':float(pen1)})
            else:
                G.add_edge(citing_author, cited_author, attr_dict={'year':int(year), 'venue':venue, 'weight':float(weight), 'author_position':int(author_pos), 'venue_score': venue_score, 'pen1':float(pen1), 'pen2':float(pen2)})
    return G
	

def addOutsiderInfo(G, file):
    epsilon = 1
    nx.set_node_attributes(G, 'outsider_info', dict(zip(G.nodes(), [epsilon]*G.number_of_nodes())))
    
    matches = {}
    with open(file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            [author, min_group_score, mean_group_score, max_group_score] = row
            #author = encodeAuthorName(author)
            	#print author
            try:
                G.node[author]['outsider_info'] = float(mean_group_score)+epsilon
                matches[author] = 1
            except KeyError:
                continue
    print "Outsiders matched %d out of %d nodes" % (len(matches), G.number_of_nodes())


	
def writeNetworkToFile(G, file):
    myf = open(file, "w")
    for edge in G.edges(data=True, keys=True):
        author1 = edge[0]
        author2 = edge[1]
        
        year = edge[3]['year']
        author_position = edge[3]['author_position']
        
        venue = edge[3]['venue']
        weight = edge[3]['weight']
        
        
        #author1 = encodeAuthorName(author1)
        #author2 = encodeAuthorName(author2)
        
        myf.write('"%s","%s",%d,"%s",%.4f,%d\n' % (author1, author2, int(year), venue, float(weight), int(author_position)))
        #myf.write(author1 + "," + author2 + "," + year + "," + venue + "," + weight + "," + author_position + "\n")
    myf.close()
    

def generateFilename(save_folder, pr_type, prod_type, out_type, outsider_rankings_file, pr_params, out_prefix):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        
    file_parts = [out_prefix]
    if pr_type == "newrank":
        file_parts.append("newrank")
    elif pr_type == "yetrank":
        file_parts.append("yetrank")
    else:
        if prod_type != "":
            file_parts.append("prodt_" + prod_type.upper())
        if out_type != "":
            if "10" in outsider_rankings_file:
                out_str = "out10_"
            elif "5" in outsider_rankings_file:
                out_str = "out5_"
            else:
                out_str = "out0_"
            file_parts.append(out_str + out_type.upper())

        file_parts.append(pr_type)
        file_parts.append("prt_" + pr_params)
    #file_parts.append(str(end_year))
    basename = save_folder + "_".join(file_parts)

    no_pr_name = basename + "_InitialPR.txt"
    first_it_name = basename + "_OneITPR.txt"
    return basename + ".txt", no_pr_name, first_it_name

def prepareData(folder, dblp_file, uniform_weight, inside_authors, Venues, in_cit_file, out_cit_file, allow_self_citations, n_pens):
#    citations_list = folder + "network_before_%d.csv" % start_year
#    icitations_list = folder + "data_in_b%d_%s.csv" % (start_year, pen_name) #3for the citation with penalties
#    ocitations_list = folder + "data_out_b%d.csv"  % start_year
#    ncitations_list = folder + "data_null.csv" ##to store guys that do not have any citation but are part of the inside network
    
    print "Creating networks weigth uniform weight = %s" % uniform_weight
    in_cit_file = folder + in_cit_file
    out_cit_file = folder + out_cit_file
    if not os.path.isfile(in_cit_file): ## read graph
        print "Did not find citation file, script is not ready to create one!"
        quit()
      #  G= createNetwork(Venues, citations_list, True, uniform_weight)	
      #  print G.number_of_edges()	
      #  G, Outside_G = getInsideOutsideGraphs(G, inside_authors)
      #  n_nodes = G.number_of_nodes()
      #  print "%d Inside Nodes, %d Outside nodes" % (G.number_of_nodes(), Outside_G.number_of_nodes())
      #  writeNetworkToFile(G, icitations_list)
      #  writeNetworkToFile(Outside_G, ocitations_list)
    else:
        G = createNetwork(Venues, in_cit_file, n_pens, uniform_weight, allow_self_citations) #3create network reading penalty column from file
        Outside_G = createNetwork(Venues, out_cit_file, 0, uniform_weight, False) ##create network without reading column penalty and without self-citations
        n_nodes = G.number_of_nodes()
        print "%d inside nodes %d outside nodes" % (G.number_of_nodes(), Outside_G.number_of_nodes())
    
    ##add dblp authors that are never cited
    graph_nodes = {n:1 for n in G.nodes()}
    for author in inside_authors:
        if author not in graph_nodes:
            G.add_node(author)
    print "%d not_cited_authors were added" % (G.number_of_nodes() - n_nodes)
    return G, Outside_G

def createGTFile(folder, best_papers, i_best_papers, matched_pubs, eval_file, G):
    filename = folder + "gt_" + eval_file
    print "GT FILE is: %s" % filename
    if os.path.isfile(filename):
        print "GT File already exists, not creating a new one"
        return
    write_file = open(filename, "a")
    for pub in matched_pubs: ##publications matched by title on the dblp file
        for i in range(len(matched_pubs[pub])):
                write_file.write('"%s","%s",%d,%.3f,%.3f\n' % (matched_pubs[pub][i], pub, 1, 1/float(len(matched_pubs[pub])), 1/float(i+1)))
    best_papers.update(i_best_papers) #dict with unmatched pubs
    counter = 0
    for pub in best_papers:
        for i in range(len(best_papers[pub])):
            if best_papers[pub][i] in G.nodes():
                counter += 1
                write_file.write('"%s","%s",%d,%.3f,%.3f\n' % (best_papers[pub][i], pub, 1, 1/float(len(best_papers[pub])), 1/float(i+1))) 
    write_file.close()
    print "Added %d by name" % counter
 
"""
def defineEvalFile(folder, start_year, end_year):
    if int(start_year) == 2099: ##special case for all data (gt file is created with filename 1900_to_2099)
        eval_list = folder + "awarded_authors_from_%d_to_%d.csv" % (1900, end_year)
    else:
        eval_list = folder + "awarded_authors_from_%d_to_%d.csv" % (start_year, end_year)
    return eval_list
""" 

def loadVenues():
    venue_scores = "../data/venues_scores.csv"
    venues_eps = 0.001
    return VenuesReader.VenuesReader(venue_scores, venues_eps)
    
##########################################