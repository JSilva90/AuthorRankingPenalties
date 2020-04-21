#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 12:05:06 2018

@author: jorge
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 15:38:26 2018

@author: jorge
"""

import networkx as nx
import csv
#import matplotlib.pyplot
import math
import copy
import argparse
import numpy as np
import os
import random
import operator
import ARankingUtils

normalize_penalties = True ##if set to true then the penalties are normalized between 0 and 1

def normalizePens(G):
    max_pen = max(nx.get_edge_attributes(G,'co_author_penalty').values())
    for edge in G.edges(data=True):
        edge[2]['co_author_penalty'] /= max_pen
    

def main(folder, dblp_file, start_year, end_year, pen_name, tests_params, out_prefix):
    uniform_weight = str2bool(tests_params[0][0]) ##the first defines the network and we are assuming that the weights are never changed for the other tests
    
    Venues = ARankingUtils.loadVenues()
    inside_venues = ARankingUtils.getInsideVenues(folder)
    eval_list = ARankingUtils.defineEvalFile(folder,start_year, end_year)

    #print "using eval list %s" % eval_list
    best_papers, i_best_papers = ARankingUtils.getAuthorsGroundTruth(eval_list)
    #print "there are %d complete best papers and %d incomplete ones" % (len(best_papers), len(i_best_papers))
    matched_best_papers, authors_info, max_pub_year = ARankingUtils.getPublicationsInfo(Venues, inside_venues, dblp_file, best_papers, i_best_papers, start_year)
    ##this iterates through the dblp file to save information for each author, it is independent of the method to be tested
    G, Outside_G = ARankingUtils.prepareData(folder, dblp_file, uniform_weight, authors_info.keys(), Venues, start_year, pen_name)
    ARankingUtils.removeGhosts(G, authors_info)# some authors are on the graph but not on authors info due to encoding errors (less than 0.1% odf the authors)
    
    if normalize_penalties:
        print "Normalizing the penalties"
        normalizePens(G)
   
    q = 0.1 #damping factor
    PR  = PageRank(q, G, authors_info, max_pub_year)

    print "Size of awarded pubs %d, failed to match %d titles" % (len(matched_best_papers), (len(best_papers)+len(i_best_papers)))
    ARankingUtils.createGTFile(folder, best_papers, i_best_papers, matched_best_papers, start_year, end_year, G) ##create the award file if it does not exist
    
    test_iterations = []
    
    
   
    for test in tests_params: ##perform each test
        
        [uni_weight, af, decay_age, tol, outsider_rankings_file, out_type, prod_type, pr_params, pr_type] = test
        if str2bool(uni_weight) != uniform_weight: 
            print "Network weights changed in middle of tests, we were NOT TRAINED for this. MAYDAY MAYDAY Emergency landing!!!!"
            quit()
        
        PR.resetPR() ##reset pagerank variables to default
        PR.setTolerance(tol)
        PR.setDecayAge(decay_age)
        PR.setAgeFunction(af)
        
        output_file, no_pr_file, first_it_file = ARankingUtils.generateFilename(folder, af, tol, decay_age, pr_type, prod_type, out_type, outsider_rankings_file, pr_params, start_year, pen_name, out_prefix)
        if os.path.isfile(output_file):
            #print "Test already exists, skipping it"
            continue
        #print "Does not exist " + output_file
        #quit()
        
        if pr_type == "newrank" or pr_type == "yetrank": ##force no outsiders and not prod
            prod_type = ""
            out_type = ""
            useYearsAverage = False ##how to get the year for a author, true use average, false use most recent
            useAge = True
            if pr_type == "newrank": ##do the necessary early steps for initial pagerank
                useVenues = False ##this true and the other one true -> yet rank
                PR.setAgeFunction("newrank") ##to be sure in case the parameter was entered wrong
            else: #in case of yet rank
                PR.setAgeFunction("yetrank")
                useVenues = True ##this true and the other one true -> yet rank
            PR.calculateNodeProbability(Venues, useYearsAverage, useAge, useVenues)
        
        PR.printSetup()       
        PR.getProductivity(prod_type) ##calculte the prod type for the method
        #print "FIM"
        #quit()
        
        oinfluence_list = ""
        if "W" in out_type or "A" in out_type or "V" in out_type:
            if os.path.isfile(folder + outsider_rankings_file): ##check if external file exists
                #print "Loading External rankings..."
                oinfluence_list = folder + outsider_rankings_file
                ARankingUtils.addOutsiderInfo(Outside_G, oinfluence_list)
            PR.getOutsiderInfluence(Outside_G, G, out_type, oinfluence_list)
            
        PR.initializePR(prod_type, out_type)
        #initialPR = sorted(PR.P.items(), key=operator.itemgetter(1),reverse=True)
        
        if pr_type == "sceas_pr":
            a = math.exp(1)
            b = 1
            my_PR = PR.getAdaptedPageRank(pr_params, a, b)
        elif pr_type == "newrank":
            my_PR = PR.getAgeRankPR("A") 
        elif pr_type == "yetrank":
            my_PR = PR.getAdaptedPageRank("W", a=1, b=0)
            #my_PR = PR.getAgeRankPR("AV")
        else: ##if no special method just use the default pr 
            a = 1
            b = 0
            my_PR = PR.getAdaptedPageRank(pr_params, a, b)
    
        #one_itPR = sorted(PR.one_it_P.items(), key=operator.itemgetter(1),reverse=True)        
        #PR.writeToFile(no_pr_file, initialPR)
        #PR.writeToFile(first_it_file, one_itPR)
        PR.writeToFile(output_file, my_PR)
        
        test_iterations.append((output_file, PR.iterations_counter))
    
    write_file = open(folder + "iterations_methods.csv", "a")
    for t in test_iterations:
        write_file.write("%s,%d\n" % (t[0], t[1]))
    write_file.close()
    
    
###############################################
## PageRank class functions
###############################################
    


class PageRank():
    def __init__(self, q, G, a_info, max_p_year):
        self.G = G
        self.q = q	  # damping factor
        self.eps = 10**(-6)  # error tolerange for convergence, default value, can change in tests
        self.authors_info = a_info ##for each authors it stores a list with [n_authors, venue_score, year] for each publication he is in

        self.max_pub_year = max_p_year
        self.age_function = self.getNewRankAge
        self.af = "newrank"
        self.iterations_counter = 0
        self.decay_age = 4.0
        
        self.P = dict() # PageRank of each node
        self.OldP = dict()
        self.one_it_P = dict() #saves the 1st iteration of the pagerank

        self.prod = dict() ##dictionary for productivity
        self.out_inf = {g : 0 for g in G.nodes()} ##dictionary for outsiders info
        self.node_prob = {g : 0 for g in G.nodes()} ##nodes_probability, used to initiate pr and distribute the damping factor and score of dangling nodes
        self.node_score = {g: 0 for g in self.G.nodes()} ##used to store the scores of the nodes
        self.node_penalty = {g: list() for g in self.G.nodes()} ##to debug the penalty process
        
        self.out_reputation_year = {g : dict() for g in G.nodes()} ##saves the outside reputation by year
        
        
    def setTolerance(self, t):
        try:
            self.eps = 10**(-float(t))
        except:
            pass
	
    def setDecayAge(self, da):
        try:
            self.decay_age = float(da)
        except:
            pass
    
    def setAgeFunction(self, af):
        if af == "yetrank":
            self.af = "yetrank"
            self.age_function = self.getYetRankAge
        else:
            self.af = "newrank"
            self.age_function = self.getNewRankAge
        
    def printSetup(self):
        print "PR instance created for %d Nodes, with damping factor %.2f, tolerance %f, decay_age %.2f and with age function %s" % (self.G.number_of_nodes(), self.q, self.eps, self.decay_age, self.af)
        
    def resetPR(self):
        self.P = dict() # PageRank of each node
        self.OldP = dict()
        self.prod = dict() ##dictionary for productivity
        self.out_inf = {g : 0 for g in self.G.nodes()}
        self.node_prob = {g : 0 for g in self.G.nodes()} ##nodes_probability, used to initiate pr and distribute the damping factor and score of dangling nodes
        self.node_score = {g: 0 for g in self.G.nodes()} ##used to store the scores of the nodes
        self.out_reputation_year = {g : dict() for g in self.G.nodes()}
        self.eps = 10**(-6)  # error tolerange for convergence, default value, can change in tests
        self.iterations_counter = 0
        self.decay_age = 4.0
        self.one_it_P = dict() #saves the 1st iteration of the pagerank
    
    def getAgeRankPR(self, params):
        """
        This is th original version that distributes the penalty by the init vector
        """
        """
        params = "A" -> new rnak
        params = "AV" -> yet rank
        
        """
        print "STARTING AgeRank with following options: %s " % (params)
        has_converged = False
        self.iterations_counter = 0
        s_j_out, s_param_out = self.getOutgoingEdges(self.G, params)
        while has_converged == False:
            self.iterations_counter += 1          
            self.OldP = copy.deepcopy(self.P)
            total_dangling_score = self.getDanglingNodesScore(s_j_out)
            print "Iteration " + str(self.iterations_counter) + "... total no outgoing links scores " + str(total_dangling_score) 
            for i in self.G.nodes(): ##estimate teh score received for each node in the next iteration
                score_term = 0.0
                for edge in self.G.in_edges(i, data=True):
                    j = edge[0]
                    attribs = edge[2]
                    ##get year score and normalize it for node
                    p_score = self.outNodeScore(params, attribs['weight'], attribs['venue_score'], attribs['year'], None)
                    #p_score /= s_param_out[j]
                    w_score = self.outNodeScore("W", attribs['weight'], attribs['venue_score'], attribs['year'], None)
                    w_score *= (1.0 - attribs['co_author_penalty'])
                    
                    try:
                        received_score = (self.OldP[j] * p_score * w_score) / s_j_out[j] 
                        received_score = (1-self.q) * received_score 
                    except:
                        received_score = 0
                    score_term += received_score
                self.node_score[i] = score_term 
            for i in self.G.nodes(): ##now that the total dangling score is final we can calculate the final scores
                dangling_term = (1-self.q) * self.node_prob[i] * total_dangling_score
                rr_term = self.node_prob[i] * self.q
                self.P[i] = rr_term + self.node_score[i] + dangling_term
                
            if self.iterations_counter == 1:
                self.one_it_P = copy.deepcopy(self.P)
            has_converged = self.converged(self.OldP, self.P, self.eps)
        return sorted(self.P.items(), key=operator.itemgetter(1),reverse=True)
    
  
        
    def getAdaptedPageRank(self, params, a=1, b=0):
        """
        This is th original version that distributes the penalty by the init vector
        """
        print "STARTING PR with following options: %s and a=%.2f and b = %.2f" % (params, a, b)
        has_converged = False
        self.iterations_counter = 0
        s_j_out, s_param_out = self.getOutgoingEdges(self.G, params)
        while has_converged == False:
            self.iterations_counter += 1           
            self.OldP = copy.deepcopy(self.P)
            total_dangling_score = self.getDanglingNodesScore(s_j_out) 
            #print "Iteration " + str(self.iterations_counter) + "... total no outgoing links scores " + str(total_dangling_score)
            for i in self.G.nodes(): ##on this version the total dangling score changes throughout the node scores calculation so we have to seperate these two loops
                score_term = 0.0
                for edge in self.G.in_edges(i, data=True):
                    j = edge[0]
                    j_out = s_param_out[j]
                    attribs = edge[2]
                    w_score = self.outNodeScore(params, attribs['weight'], attribs['venue_score'], attribs['year'], i)
                    ##apply weight to penalty
                    w_score *= (1.0 - attribs['co_author_penalty'])
                    try:
                        received_score = (1-self.q) * ((self.OldP[j] + b) * (w_score / j_out))
                    except: ## in case the penalty descreases the link to 0
                        received_score = 0
                    received_score /= a ## for sceas otherwise it's always 1.0
                    score_term += received_score
                self.node_score[i] = score_term
                
            for i in self.G.nodes(): ##now that the total dangling score is final we can calculate the final scores
                dangling_term = (1-self.q) * self.node_prob[i] * total_dangling_score
                rr_term = self.node_prob[i] * self.q
                self.P[i] = rr_term + self.node_score[i] + dangling_term
            

            if self.iterations_counter == 1: ##save the one iteration PR
                self.one_it_P = copy.deepcopy(self.P)
            has_converged = self.converged(self.OldP, self.P, self.eps)
        return sorted(self.P.items(), key=operator.itemgetter(1),reverse=True)        

        
    
    def initializePR(self, prod_t, out_t):
        """
        Initializes the page rank. IF use productivity is on, it uses the prod vector
        else it uses the node_prob which should already have been calculated before using the calculateNodeProbability
        """
        
        useProductivity = False
        if "A" in prod_t or "P" in prod_t or "V" in prod_t:
            useProductivity = True
        
        useOutsiders = False
        if "A" in out_t or "W" in out_t or "V" in out_t:
            useOutsiders = True
        
        if not useProductivity and not useOutsiders and sum(self.node_prob.values()) == 0:
            print "Node prob not pre-calculated when useProd and useOutsiders = False. Adding Uniform value"
            for n in self.node_prob:
                self.node_prob[n] = 1 / float(self.G.number_of_nodes())
           
        print "Initializing PR with useprod = %s, type (%s) and useout = %s type (%s)" % (useProductivity, prod_t, useOutsiders,out_t)
        for node in self.G.nodes():
            if useProductivity:
                if useOutsiders:
                    self.node_prob[node] = (self.prod[node] + self.out_inf[node])/2
                else:
                    self.node_prob[node] = self.prod[node]
            else: ##if else the node_prob should be already initiated with the other function
                if useOutsiders:
                    self.node_prob[node] = self.out_inf[node] 
            self.P[node] = self.node_prob[node]
    
    def getOutgoingEdges(self, G, out_params):
        """
        Always returns a dict with the total weight out of the node and another dict based on the out_params string.
        IF WAV, it returns weight * age * venue for each node, if WV weight * venue...
        """
        s_j_out = {g : 0.0 for g in G.nodes()}
        s_j_params = {g : 0.0 for g in G.nodes()}
            
        for j in G.nodes():
            for edge in G.out_edges(j, data=True):
                node = edge[1]
                attribs = edge[2]
                
                weight = attribs['weight']
                param_score = self.outNodeScore(out_params, attribs['weight'], attribs['venue_score'], attribs['year'], node)
                ##apply weights penalty
                weight *= (1.0 - attribs['co_author_penalty'])
                param_score *= (1.0 - attribs['co_author_penalty'])
                
                s_j_out[j] += weight
                s_j_params[j] += param_score
                
        return s_j_out, s_j_params
                        
    
    def outNodeScore(self, out_params, weight, venue_score, year, node):
        """
        We have to receive the node in the receiving end to calculate the outsiders pagerank
        """
        out_score = 0.0
        if "W" in out_params:
            out_score = weight
        if "A" in out_params:
            if out_score == 0:
                out_score = self.age_function(year)
            else:
                out_score *= self.age_function(year)
        if "V" in out_params:
            if out_score == 0:
                out_score = venue_score
            else:
                out_score *= venue_score
        if "O" in out_params:
            if out_score == 0:
                out_score = self.calculateOutInfluenceYearScore(node, year)
            else:
                out_score *= self.calculateOutInfluenceYearScore(node, year)
        return out_score
    
    def calculateOutInfluenceYearScore(self, node, year):
        """
        Returns the sum of the outsider score of the node until a certain year
        """
        return sum([self.out_reputation_year[node][y] for y in self.out_reputation_year[node] if y <= year]) + 0.01 ##sum eps to have a minimum value for 0
    
    def getOutsiderInfluence(self, Outside_G, G, out_params, oinfluence):
        """
        gets the outsider influence considering several parameters on the out_params
        if out_params = W, only weight is consideredm if WV weight * venue etc...
        """
        s_j_out, s_j_params = self.getOutgoingEdges(Outside_G, out_params)

        print "Getting Outsider Influence with parameters %s and using outsider rank file %s" % (out_params, oinfluence)
        check = {}
        for edge in Outside_G.edges(data=True):
            outsider = edge[0]
            insider  = edge[1]
            attribs  = edge[2]
			 
            if outsider not in check:
                check[outsider] = 0.0
            
            w = self.outNodeScore(out_params, attribs['weight'], attribs['venue_score'], attribs['year'], None)
            w /= s_j_params[outsider]

            check[outsider] += w
            if oinfluence != "": ##if external ranking multiply
                w *= Outside_G.node[outsider]['outsider_info']

            if insider not in self.out_inf: 
                self.out_inf[insider] = 0.0
            self.out_inf[insider] += w
            
            if insider not in self.out_reputation_year:
                self.out_reputation_year[insider] = dict()
            if int(attribs['year']) not in self.out_reputation_year[insider]: ##save scores received per year
                self.out_reputation_year[insider][int(attribs['year'])] = 0.0
            self.out_reputation_year[insider][int(attribs['year'])] += w
            
        total_influence = sum(self.out_inf.values())	
        for i in G.nodes():
            if i in self.out_inf:
                self.out_inf[i] /= total_influence
            else:
                self.out_inf[i] = 0
        for i in check: ##just a safety check to be sure that the full percentage of the outsider's feature is being distributed
            if abs(check[i] - 1.0) > 0.000002:
                print "Node %s only sent %.6f part of his score to the inside authors" % (i, check[i])
    
         
    def prod_function(self, prod_type, n_authors, venue_score, year):
        """
        Looking at the input for the prod function it creates the prod function
        IF P it adds the productivity if A if adds age if V it adds venues. Prod * venues= PA, if none it returns 0 
        """
        prod_score = 0.0
        if "P" in prod_type:
            prod_score = 1 / float(n_authors)
        if "A" in prod_type:
            if prod_score == 0:
                prod_score = self.age_function(year)
            else:
                prod_score *= self.age_function(year)
        if "V" in prod_type:
            if prod_score == 0:
                prod_score = venue_score
            else:
                prod_score *= venue_score
        
        #print "prod type: %s , prod score %f" % (prod_type, prod_score)
        return prod_score
    

    def getProductivity(self, prod_type):
        """
        This is a generic function to get the productivity vector     
        """
        self.prod = {node : 0 for node in self.G.nodes()}
        
        print "Getting productivity with prod type %s" % prod_type
        
        for author in self.authors_info:
            for info in self.authors_info[author]:
                self.prod[author] += self.prod_function(prod_type, info[0], info[1], info[2])
                #if "feiping" in author.lower():
                #    print "prod %f, %s, %d, %s" % (self.prod[author], author, self.max_pub_year, info[2])

        total_prod = sum(self.prod.values())
        if total_prod == 0: ##the uniform case, return 0 for the prod_function
            for i in self.prod:
                self.prod[i] = 1 / float(self.G.number_of_nodes())
        else:

            for i in self.prod:
                self.prod[i] /= float(total_prod)
        print "Total prod = %.5f" % sum(self.prod.values())

    
    def getDanglingNodesScore(self, out_degree_dict):
        """
        Returns the total score of all the dangling nodes.
        Needs to get an out_degree_dict that has the out degree value of each node
        """
        dangling_nodes_score = 0.0
        for node in out_degree_dict:
            if out_degree_dict[node] == 0: ##dangling node
                dangling_nodes_score += self.OldP[node]
        return dangling_nodes_score
    
    def calculateNodeProbability(self, Venues, useYearsAverage, useAge, useVenues):
        """
        Calculates the probability vectors for the ones, similar to productivity but adapted to NEWRank and YETRank
        """
        print "Calculate Node probability using average years for node = %s, using age = %s and using venues = %s" % (useYearsAverage, useAge, useVenues)
        for node in self.G.nodes():
            self.node_prob[node] = 0
            if useAge:
                self.node_prob[node] = self.age_function(self.getNodeAge(node, useYearsAverage))
            if useVenues:
                if self.node_prob[node] == 0:
                    self.node_prob[node] = self.getNodeVenueScore(node)
                else:
                    self.node_prob[node] *= self.getNodeVenueScore(node)
        
        total = sum(self.node_prob.values())
        for node in self.node_prob:
            self.node_prob[node] /= float(total)
        print "Total node prob = %.5f" % sum(self.node_prob.values())
        
    
    def getNodeVenueScore(self, node):
        """
        Returns the average score of the venues where an author published
        """
        if len(self.authors_info[node]) == 0:
            return 0.001
        return np.average([x[1] for x in self.authors_info[node]])      
        
    
    def getNodeAge(self, node, useAverage):
        """
        Returns the age of a node. If use average, node's age = avg(pub_years), else node's age
        """
        if len(self.authors_info[node]) == 0:
            return 15 ##default max year
        if useAverage:
            return int(round(np.average([x[2] for x in self.authors_info[node]]), 0))
        else:
            return max([x[2] for x in self.authors_info[node]])
        
        
    def converged(self, OldP, P, epsilon):
        for key in OldP.keys():
            if(math.fabs(OldP[key] - P[key]) > epsilon):
                #print "Didn't converge (" + str(round(math.fabs(OldP[key] - P[key]),7)) + " > " + str(epsilon) + ")"
                return False
        return True
    
    def getNewRankAge(self, year):
        return math.exp(-((self.max_pub_year - year) / self.decay_age))

    def getYetRankAge(self, year):
        return (math.exp(-((self.max_pub_year - year) / self.decay_age))) / float(self.decay_age)
    
    def getPageRankOnlyInit(self):
        return sorted(self.P.items(), key=operator.itemgetter(1),reverse=True)
    
    def writeToFile(self, file, my_PR):
        ranking_f = open(file, "w")		
        for i in my_PR:
            name	  = i[0]
            pred_rank = i[1]
			
            """
            if name in inside_authors:
                try:
                    real_rank = str(authors_real_eval[name])
                except KeyError:
                    real_rank = "0"
                    #print id + " " + name + " " + str(i[1])
                ranking_f.write(name + "," + pred_rank + "," + real_rank + "\n")
            """
            ranking_f.write('"%s",%.14f\n' % (name, pred_rank))
        ranking_f.close()
        print "Ranking written to " + file
        


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compute our PageRank.')
    parser.add_argument('-f', action='store', type=str, help='folder that contains the data', required=True)
    #parser.add_argument('-dblp', action='store', type=str, help='dblp file for productivity',required=True)
    parser.add_argument('-tests', action='store', type=str, help='csv file with tests', required=True)
    parser.add_argument('-syear', action='store', type=int, help='define start year', required=True)
    parser.add_argument('-eyear', action='store', type=int, help='define end year', required=True)
    #parser.add_argument('-cit_pen_file', action='store', type=str, help='citation file with penalty column', required=True)
    parser.add_argument('-pen_name', action='store', type=str, help='define penalty name for the tests in the results file', required = True)
    parser.add_argument('-test_name', action='store', type=str, help='define the prefix for the output files', required = True)
    args = parser.parse_args()
    
    param_tests = []
    with open(args.tests, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            if len(row) != 9: 
                print "incorrect test files, if should have 9 csv columns: " + str(row)
                quit()
            param_tests.append(row)
            
    random.shuffle(param_tests) ##in case we run tests in parallel they do not follow the same order
    #dblp_file = args.dblp
    dblp_file = "../data/dblp_12.2017.txt"
    out_prefix = args.test_name
    folder = args.f
    end_year = args.eyear
    start_year = args.syear
    #cit_file = args.cit_pen_file
    pen_name = args.pen_name
    main(folder, dblp_file, start_year, end_year, pen_name, param_tests, out_prefix)
