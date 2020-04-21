#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 11:36:41 2018

@author: jorge
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class VenuesReader():
    """
    it receives a filename to get the scores
    """
    def __init__(self, filename, eps):
        self.epsilon = eps
        self.missing_year = 0
        self.filename = filename
        self.associations = dict() ##associates the name oof the conferences in the network to the name of the conference on scopus. required to get the scores
        self.venue_scores = dict() ##the scores
        self.normalized_scores = dict() ##standardizes the scores per year and has a defined x year whcih is a standardized representation for years when the conference has no score
        self.__readAssociations()
        self.__readScores()
        self.__calculateNormalizedScores()
        
    def __readAssociations(self):
        df = pd.read_csv(self.filename, names=['kdd_name', 'url', 'scopus_name', 'year', 'score'])
        assoc = set(zip(list(df['kdd_name'].values), list(df['scopus_name'].values)))
        self.associations = {a[0] : a[1] for a in assoc}
        
    def __readScores(self):
        df = pd.read_csv(self.filename, names=['kdd_name', 'url', 'scopus_name', 'year', 'score'])
        df2 = df[['scopus_name', 'year', 'score']] ##ignore the kdd_name and url columns we only need them for associations which we already obtained
        df2 = df2.drop_duplicates() ##since some kdd venues are mapped into the same venue, we have duplicate scores which we can remove
        #self.scores_df = df2
        scores = zip(list(df2['scopus_name']), list(df2['year']), list(df2['score']))
        for s in scores:
            venue, year, score = s
            if venue not in self.venue_scores:
                self.venue_scores[venue] = dict()
            self.venue_scores[venue][year] = score
            
    def __calculateNormalizedScores(self):
        """
        saves the standard scores per year for every conference
        also for each conference creates an x-year which is the average of the scores
        the x-year should be used for years when we have no information
        the x-year is also standardized
        """
        year_scores = {0 : []}
        for venue in self.venue_scores:
            v_scores = []
            for year in self.venue_scores[venue]:
                v_scores.append(self.venue_scores[venue][year])
                if year not in year_scores:
                    year_scores[year] = []
                year_scores[year].append(self.venue_scores[venue][year])
            x_year = np.average(np.array(v_scores))
            self.venue_scores[venue][0] = x_year
            year_scores[0].append(x_year)
        
        ##for standardization
        #year_metrics = {x : (np.average(np.array(year_scores[x])), np.std(np.array(year_scores[x]))) for x in year_scores}
        ##for normalization
        year_metrics = {x: (max(year_scores[x]), min(year_scores[x])) for x in year_scores}
        
        #print year_metrics
        
        for venue in self.venue_scores:
            self.normalized_scores[venue] = dict()
            for year in self.venue_scores[venue]:
                #self.standard_scores[venue][year] = round((self.venue_scores[venue][year] - year_metrics[year][0]) / year_metrics[year][1],5)
                #self.normalized_scores[venue][year] = (self.venue_scores[venue][year] - year_metrics[year][1]) / (year_metrics[year][0] - year_metrics[year][1]) + eps
                self.normalized_scores[venue][year] = (self.venue_scores[venue][year] - year_metrics[year][1] + self.epsilon) / (year_metrics[year][0] - year_metrics[year][1] + self.epsilon)
        
    def getVenueName(self, v_name):
        """
        Returns the name of the venue on the scopus
        """
        if v_name not in self.associations:
            #print "Venue %s does not exist on the associations" % v_name
            return None
        return self.associations[v_name]
    
    def getVenueScores(self, v_name, normalized=True, scopus_name=False):
        """
        Returns the scores per year of the venue
        if scopus_name = true then it assumes that it is already a venue name from scopus, 
        otherwise it gets the association value before getting the scores
        if normalized returns the normalized values
        """
        if not scopus_name:
            v_name = self.getVenueName(v_name)
            if not v_name:
                return None   
        #s_df = self.scores_df.loc[self.scores_df['scopus_name'] == v_name]
        #scores = zip(list(s_df['year'].values),list(s_df['score'].values))
        if normalized:
            return self.normalized_scores[v_name]
        return self.venue_scores[v_name]
    
    def getVenueScoreYear(self, v_name, year, normalized=True, scopus_name=False):
        """
        Returns the score of the venue in a certain year        
        if scopus_name = true then it assumes that it is already a venue name from scopus, 
        otherwise it gets the association value before getting the scores
        if normalized returns the normalized values
        """
        if not scopus_name:
            v_name = self.getVenueName(v_name)
            if not v_name:
                return None
        if v_name not in self.venue_scores:
            #print "Venue %s does not have any score" % v_name
            return None
        if year not in self.venue_scores[v_name]:
            #print "Venue %s does not have a score for year %d" % (v_name, year)
            if normalized:
                return self.normalized_scores[v_name][0]
            return self.venue_scores[v_name][0]
        if normalized:
            return self.normalized_scores[v_name][year]
        return self.venue_scores[v_name][year]
        
        #s_df = self.scores_df.loc[(self.scores_df['scopus_name'] == v_name) & (self.scores_df['year'] == year)]
        #if s_df.empty:
            
            #print "Either conference %s does not exist, or it does not have a score for year %d" % (v_name, year)
         #   return None
        #return s_df['score'].values[0] ##there should be only one score per conference and year
        
    
    
    
    
    
        

    