#!/bin/bash


#conf_name=("national conference on artificial intelligence_international conference on management of data_user interface software and technology_symposium on the theory of computing_operating systems design and implementation_international conference on computer communications_ieee symposium on security and privacy" "national conference on artificial intelligence_international joint conference on artificial intelligence_international conference on machine learning_meeting of the association for computational linguistics_computer vision and pattern recognition_international conference on computer vision" "knowledge discovery and data mining_conference on information and knowledge management_symposium on principles of database systems_international conference on management of data_very large data bases_international world wide web conferences_international acm sigir conference on research and development in information retrieval" "foundations of computer science_symposium on discrete algorithms_symposium on the theory of computing" "programming language design and implementation_foundations of software engineering_international conference on software engineering_operating systems design and implementation_symposium on operating systems principles" "international conference on computer communications_networked systems design and implementation_acm special interest group on data communication_acm ieee international conference on mobile computing and networking_measurement and modeling of computer systems")
#conf_sigla=("AAAI_SIGMOD_UIST_STOC_OSDI_INFOCOM_S&P" "AAAI_IJCAI_ICML_ACL_CVPR_ICCV" "KDD_CIKM_PODS_SIGMOD_VLDB_WWW_SIGIR" "FOCS_SODA_STOC" "PLDI_FSE_ICSE_OSDI_SOSP" "INFOCOM_NSDI_SIGCOMM_MOBICOM_SIGMETRICS")





conf_name=("knowledge discovery and data mining_conference on information and knowledge management_symposium on principles of database systems_international conference on management of data_very large data bases_international world wide web conferences_international acm sigir conference on research and development in information retrieval")
conf_sigla=("KDD_CIKM_PODS_SIGMOD_VLDB_WWW_SIGIR") 
	
validadion_year=2016
test_year=2014



for i in "${!conf_name[@]}"; do
	echo "${conf_name[$i]} ${conf_sigla[$i]}"
	#rm data/${conf_sigla[$i]}/results_2/FULLNET_sceas_prt_W*
	#rm data/${conf_sigla[$i]}/results_2/sceas_prt_W*

	#mv data/${conf_sigla[$i]}/results/* data/${conf_sigla[$i]}/results_2/
	#mv data/${conf_sigla[$i]}/results_2/* data/${conf_sigla[$i]}/results/
	#rm data/${conf_sigla[$i]}/results_2/

	#rm ../data/${conf_sigla[$i]}/metrics/otarios_v3/*.csv
	#cp ../data/${conf_sigla[$i]}/results/otarios_v2/newrank_2099.txt ../data/${conf_sigla[$i]}/results/otarios_v3/PEN_DIST_INIT/
	#cp ../data/${conf_sigla[$i]}/results/otarios_v2/newrank_2099_InitialPR.txt ../data/${conf_sigla[$i]}/results/otarios_v3/PEN_DIST_INIT/
	#for f in ../data/${conf_sigla[$i]}/results/otarios_v3/PEN_DIST_INIT/*teste_Initial*; do mv "$f" "${f/teste_InitialPR/start}";done
	#rm ../data/${conf_sigla[$i]}/results/otarios_v3/PEN_DIST_INIT/*Initial*
	#rm ../data/${conf_sigla[$i]}/results/otarios_v3/PEN_DIST_INIT/*pen1.txt

	#for f in ../data/${conf_sigla[$i]}/results/otarios_v3/PEN_DIST_INIT_NORM/*teste_Initial*; do mv "$f" "${f/teste_InitialPR/start}";done
	#rm ../data/${conf_sigla[$i]}/results/otarios_v3/PEN_DIST_INIT_NORM/*Initial*
	#rm ../data/${conf_sigla[$i]}/results/otarios_v3/PEN_DIST_INIT_NORM/*pen1.txt

	#for f in ../data/${conf_sigla[$i]}/results/otarios_v3/PEN_NO_DIST/*teste_Initial*; do mv "$f" "${f/teste_InitialPR/start}";done
	#rm ../data/${conf_sigla[$i]}/results/otarios_v3/PEN_NO_DIST/*Initial*
	#rm ../data/${conf_sigla[$i]}/results/otarios_v3/PEN_NO_DIST/*pen1.txt


	#for f in ../data/${conf_sigla[$i]}/results/otarios_v3/PEN_PR/*teste_Initial*; do mv "$f" "${f/teste_InitialPR/start}";done
	#rm ../data/${conf_sigla[$i]}/results/otarios_v3/PEN_PR/*Initial*



	

#	./prepare_venue.sh "${conf_name[$i]}" "${conf_sigla[$i]}" &
#	rm -r data/${conf_sigla[$i]}/results
#	rm data/${conf_sigla[$i]}/res.csv
	#mkdir ../data/${conf_sigla[$i]}/results/otarios_v2
	#mkdir ../data/${conf_sigla[$i]}/results/otarios_v3
#	mv ../data/${conf_sigla[$i]}/results/*.txt ../data/${conf_sigla[$i]}/results/otarios_v2/
	#mkdir ../data/${conf_sigla[$i]}/metrics
	#mkdir ../data/${conf_sigla[$i]}/metrics/otarios_v2
	#mkdir ../data/${conf_sigla[$i]}/metrics/otarios_v3
	#mv ../data/${conf_sigla[$i]}/res_* ../data/${conf_sigla[$i]}/metrics/otarios_v2/

# 	
	#python 
#	./prepare_venue.sh "${conf_name[$i]}" "${conf_sigla[$i]}" $test_year $validadion_year &
	./prepare_venue.sh "${conf_name[$i]}" "${conf_sigla[$i]}" $test_year $validadion_year
#	./clean_files.sh "${conf_name[$i]}" "${conf_sigla[$i]}" $test_year $validadion_year
#	./clean_results.sh "${conf_name[$i]}" "${conf_sigla[$i]}" $test_year $validadion_year
#	./get_metrics.sh "${conf_name[$i]}" "${conf_sigla[$i]}" $test_year $validadion_year
#	./get_centralities.sh "${conf_name[$i]}" "${conf_sigla[$i]}" $test_year $validadion_year &

done

#echo "$in_n"
#echo "$out_n"
#echo "$gt_authors"


