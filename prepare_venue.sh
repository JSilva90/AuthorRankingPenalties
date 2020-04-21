#!/bin/bash

confname=$1
shortname=$2
testyear=$3
valyear=$4
MAXYEAR=2999

##creting networks
#python network_creator.py "$confname" ../data/$shortname/network_before_2012.csv ../data/$shortname/total_pids_2012.csv 2012
#wait
#echo "../data/$shortname/network_before_2012.csv created"
#python network_creator.py "$confname" ../data/$shortname/network_before_2014.csv ../data/$shortname/total_pids_2014.csv 2014
#wait
#echo "../data/$shortname/network_before_2014.csv created"
#python network_creator.py "$confname" ../data/$shortname/network_before_2016.csv ../data/$shortname/total_pids_2016.csv 2016
#wait
#echo "../data/$shortname/network_before_2016.csv created"
#python network_creator.py "$confname" ../data/$shortname/network_before_2099.csv ../data/$shortname/total_pids_2099.csv 2099
#wait
#echo "../data/$shortname/network_before_2099.csv created"
#echo "Creating CoAuthorship network"
#python coauthor_network_creator.py "$confname" ../data/$shortname/coauthorship.csv



#externalRanking Test
#echo "Creating External Ranking"
#python getExternalRanking.py ../data/$shortname/network_before_2012.csv ../data/author_info.json 2012 5 ../data/$shortname/external_rankings_5_2012.csv
wait
#echo "../data/$shortname/external_rankings_5_2012.csv created"
#python getExternalRanking.py ../data/$shortname/network_before_2012.csv ../data/author_info.json 2012 10 ../data/$shortname/external_rankings_10_2012.csv
wait
#echo "../data/$shortname/external_rankings_10_2012.csv created"
#python getExternalRanking.py ../data/$shortname/network_before_2014.csv ../data/author_info.json 2014 5 ../data/$shortname/external_rankings_5_2014.csv
wait
#echo "../data/$shortname/external_rankings_5_2014.csv created"
#python getExternalRanking.py ../data/$shortname/network_before_2014.csv ../data/author_info.json 2014 10 ../data/$shortname/external_rankings_10_2014.csv
wait
#echo "../data/$shortname/external_rankings_10_2014.csv created"
#python getExternalRanking.py ../data/$shortname/network_before_2016.csv ../data/author_info.json 2016 5 ../data/$shortname/external_rankings_5_2016.csv
wait
#echo "../data/$shortname/external_rankings_5_2016.csv created"
#python getExternalRanking.py ../data/$shortname/network_before_2016.csv ../data/author_info.json 2016 10 ../data/$shortname/external_rankings_10_2016.csv
wait
#echo "../data/$shortname/external_rankings_10_2016.csv created"
#python getExternalRanking.py ../data/$shortname/network_before_2099.csv ../data/author_info.json 2099 5 ../data/$shortname/external_rankings_5_2099.csv
wait
#echo "../data/$shortname/external_rankings_5_2099.csv created"
#python getExternalRanking.py ../data/$shortname/network_before_2099.csv ../data/author_info.json 2099 10 ../data/$shortname/external_rankings_10_2099.csv
wait
#echo "../data/$shortname/external_rankings_10_2099.csv created"

##Creating GT files
#echo "Creating GT files"

#python best_papers_parser.py $shortname ../data/$shortname 2012 2099
wait
#python best_papers_parser.py $shortname ../data/$shortname 2014 2099
wait
#python best_papers_parser.py $shortname ../data/$shortname 2016 2099
wait
#python best_papers_parser.py $shortname ../data/$shortname 1900 2099
wait
#echo "Created awards gt"

#python GTMorePubsVenue.py ../data/$shortname/venue_authors.txt 2012 2099
wait
#python GTMorePubsVenue.py ../data/$shortname/venue_authors.txt 2014 2099
wait
#python GTMorePubsVenue.py ../data/$shortname/venue_authors.txt 2016 2099
wait
#echo "Created most pubs gt"



##ADD the penalties to the networks...
#python estimateCoAuthorPenaltyParallel.py ../data/$shortname/coauthorship.csv ../data/$shortname/data_in_b2099.csv "D" "dist"
wait
#python estimateCoAuthorPenaltyParallel.py ../data/$shortname/coauthorship.csv ../data/$shortname/data_in_b2099.csv "A" "age"
wait
#python estimateCoAuthorPenaltyParallel.py ../data/$shortname/coauthorship.csv ../data/$shortname/data_in_b2099.csv "F" "freq"
wait
#python estimateCoAuthorPenaltyParallel.py ../data/$shortname/coauthorship.csv ../data/$shortname/data_in_b2099.csv "DA" "dist_age"
wait
#python estimateCoAuthorPenaltyParallel.py ../data/$shortname/coauthorship.csv ../data/$shortname/data_in_b2099.csv "DF" "dist_freq"
wait
#python estimateCoAuthorPenaltyParallel.py ../data/$shortname/coauthorship.csv ../data/$shortname/data_in_b2099.csv "FA" "freq_age"
wait
#python estimateCoAuthorPenaltyParallel.py ../data/$shortname/coauthorship.csv ../data/$shortname/data_in_b2099.csv "FAD" "dist_freq_age"
wait

##time to test the awards:
#echo "Starting tests for year 2012"
#python authorRanking.py -f ../data/$shortname/ -dblp ../data/dblp_12.2017.txt -tests soa_tests_2012.csv -syear 2012 -eyear 2099
wait
#echo "Starting tests for year 2014"
#python authorRanking.py -f ../data/$shortname/ -dblp ../data/dblp_12.2017.txt -tests soa_tests_2014.csv -syear 2014 -eyear 2099
wait
#echo "Starting tests for year 2016"
#python authorRanking.py -f ../data/$shortname/ -dblp ../data/dblp_12.2017.txt -tests soa_tests_2016.csv -syear 2016 -eyear 2099
wait
#echo "Starting tests for all data"
#python authorRankingWithSelfCitations.py -f ../data/$shortname/ -dblp ../data/dblp_12.2017.txt -tests soa_tests.csv -syear 2099 -eyear 2099 -pen_name "selfcit"
#python authorRankingNoPens.py -f ../data/$shortname/ -test_name "baselines" -tests soa_tests.csv -syear 2099 -eyear 2099 -pen_name "dist" &

#python authorRanking.py -f ../data/$shortname/ -dblp ../data/dblp_12.2017.txt -tests soa_small.csv -syear 2099 -eyear 2099 -pen_name "dist"
#python authorRanking.py -f ../data/$shortname/ -dblp ../data/dblp_12.2017.txt -tests soa_small.csv -syear 2099 -eyear 2099 -pen_name "age"
#python authorRanking.py -f ../data/$shortname/ -dblp ../data/dblp_12.2017.txt -tests soa_small.csv -syear 2099 -eyear 2099 -pen_name "freq"
#python authorRanking.py -f ../data/$shortname/ -dblp ../data/dblp_12.2017.txt -tests soa_small.csv -syear 2099 -eyear 2099 -pen_name "dist_age"
#python authorRanking.py -f ../data/$shortname/ -dblp ../data/dblp_12.2017.txt -tests soa_small.csv -syear 2099 -eyear 2099 -pen_name "dist_freq"
#python authorRanking.py -f ../data/$shortname/ -dblp ../data/dblp_12.2017.txt -tests soa_small.csv -syear 2099 -eyear 2099 -pen_name "freq_age"
#python authorRanking.py -f ../data/$shortname/ -dblp ../data/dblp_12.2017.txt -tests soa_small.csv -syear 2099 -eyear 2099 -pen_name "dist_freq_age"

python authorRankingNormPens.py -f ../data/$shortname/ -test_name "Cocit_InitPen" -tests soa_tests.csv -syear 2099 -eyear 2099 -pen_name "cocit_naive" &
python authorRankingNormPens.py -f ../data/$shortname/ -test_name "Cocit_InitPen" -tests soa_tests.csv -syear 2099 -eyear 2099 -pen_name "cocit_min" &
python authorRankingNormPens.py -f ../data/$shortname/ -test_name "Cocit_InitPen" -tests soa_tests.csv -syear 2099 -eyear 2099 -pen_name "cocit_avg" &
python authorRankingNormPens.py -f ../data/$shortname/ -test_name "Cocit_InitPen" -tests soa_tests.csv -syear 2099 -eyear 2099 -pen_name "cocit_max" &


python authorRankingWeightsPenalty.py -f ../data/$shortname/ -test_name "Cocit_WeightPen" -tests soa_tests.csv -syear 2099 -eyear 2099 -pen_name "cocit_naive" &
python authorRankingWeightsPenalty.py -f ../data/$shortname/ -test_name "Cocit_WeightPen" -tests soa_tests.csv -syear 2099 -eyear 2099 -pen_name "cocit_min" &
python authorRankingWeightsPenalty.py -f ../data/$shortname/ -test_name "Cocit_WeightPen" -tests soa_tests.csv -syear 2099 -eyear 2099 -pen_name "cocit_avg" &
python authorRankingWeightsPenalty.py -f ../data/$shortname/ -test_name "Cocit_WeightPen" -tests soa_tests.csv -syear 2099 -eyear 2099 -pen_name "cocit_max" &
wait


#python convert_results.py "../data/$shortname/results/"
wait
##get results for test considering awared papers
#python getMetricsOutput.py "../data/$shortname/results/" "../data/$shortname/gt_awards_authors_2012_to_2099.csv" "2012" > "../data/$shortname/res_awards_2012.csv"
wait
#python getMetricsOutput.py "../data/$shortname/results/" "../data/$shortname/gt_awards_authors_2014_to_2099.csv" "2014" > "../data/$shortname/res_awards_2014.csv"
wait
#python getMetricsOutput.py "../data/$shortname/results/" "../data/$shortname/gt_awards_authors_2016_to_2099.csv" "2016" > "../data/$shortname/res_awards_2016.csv"
wait
#python getMetricsOutput.py "../data/$shortname/results/otarios_v3/" "../data/$shortname/gt_awards_authors_1900_to_2099.csv" "2099" > "../data/$shortname/metrics/otarios_v3/all_res_awards_2099.csv"
wait

#python getMetricsOutput.py "../data/$shortname/results/" "../data/$shortname/gt_awards_authors_1900_to_2099.csv" "2099" > "$shortname_res_awards_2099.csv"
wait
#python getMetricsOutput.py "../data/$shortname/results/" "../data/$shortname/GT_mostpubs_2012_2099.csv" "2012" > "../data/$shortname/res_morepubs_2012.csv"
wait
#python getMetricsOutput.py "../data/$shortname/results/" "../data/$shortname/GT_mostpubs_2014_2099.csv" "2014" > "../data/$shortname/res_morepubs_2014.csv"
wait
#python getMetricsOutput.py "../data/$shortname/results/" "../data/$shortname/GT_mostpubs_2016_2099.csv" "2016" > "../data/$shortname/res_morepubs_2016.csv"
wait




#python getMetricsOutput.py "../data/$shortname/results/" "../data/$shortname/gt_awards_authors_${testyear}_to_${valyear}.csv" > "../data/$shortname/res_awards_${testyear}_to_${valyear}.csv"
#wait
##get results for test considering most publications
#python getMetricsOutput.py "../data/$shortname/results/" "../data/$shortname/GT_mostpubs_${testyear}_${valyear}.csv" > "../data/$shortname/res_mostpubs_${testyear}_to_${valyear}.csv"
#wait


#######

#echo "Creating network for eigenfactor ( $shortname)"
#python eigenfactor_network_creation.py "$confname" data/$shortname/ ##need to adapt this to network by years if we want to compare
#wait


#echo "Starting tests:..."


#wait
#echo "Starting eigenfactor test"
#python eigenfactor_rank.py data/$shortname/
#wait
#python countRank.py "$confname" data/$shortname/
#wait
#echo "Starting Full Net SOA tests"
#python fullNetworkAuthorRanking.py -f data/$shortname/ -dblp data/dblp_12.2017.txt -tests soa_tests_only.csv
#wait
