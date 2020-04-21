# AuthorRankingPenalties

This code ranks authors using multiple author ranking algorithms (check [1,2,3] for more details). Additionally it presented the option to penalise "friendly citations" which improve the overall author ranking[3]. This code was built to mass test several algorithms in different datasets. The code includes the script to process the complete pipeline of testing a set of conferences from the DBLP dataset. 

The bash script grouped_conf.sh starts the tests. Description about every script is provided in the prepare_venue.sh file and also in each file's code. The current approach requires data from the DBLP dataset [https://www.aminer.org/citation], best paper award information [already included in the data folder and extracted from: https://jeffhuang.com/best_paper_awards.html], venues score [included in data folder and extracted from: https://www.scopus.com/home.uri], and author information [can be extracted from the DBLP file, current file in data is just a sample since the complete file is too large to add to git hub]. The soa_test.csv contains the parameters that define each author ranking test and penalties applied. Each line represents a different text.


This code was used to produce the following publications:

[1] Jorge Silva, David Aparício, and Fernando Silva. "OTARIOS: OpTimizing author ranking with insiders/outsiders subnetworks." International Conference on Complex Networks and their Applications. Springer, Cham, 2018.

[2] Jorge Silva, David Aparício, and Fernando Silva. "Feature-enriched author ranking in incomplete networks." Applied Network Science 4.1 (2019): 74.

[3] Jorge Silva, David Aparício, Pedro Ribeiro, and Fernando Silva. "FOCAS: penalising friendly citations to improve author ranking." Proceedings of the 35th Annual ACM Symposium on Applied Computing. 2020.



For more details on the code or any other information, feel free to contact me at: jorge.m.silva@inesctec.pt
