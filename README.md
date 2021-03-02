# ZYELL---NCTU-Network-Anomaly-Detection-Challenge
Here constains：Training model, Pre-processed code, Training and Testing code  

# ICASSP 2021 ZYELL-NCTU NAD CHALLENGE #
##NAD2021 challenge official website : https://nad2021.nctu.edu.tw/  
### Syslog traffics dataset from ZYELL   ###

@2021 IEEE International Conference on Acoustics, Speech and Signal Processing 
              6-11 June 2021 • Toronto, Ontario, Canada
	      
#//-------------------------------------------------------------------------------//
#//-------------------------------------------------------------------------------//
#//  (C) Copyright Optimum Application-Specific Integrated System Lab Lab (OASIS) //
#//                            All Right Reserved                                 //
#//-------------------------------------------------------------------------------//
#//                        Arthor ： Shao-Wen, Cheng                              //
#//                                                                               //
#//                          Release version : v1.0                               //
#//-------------------------------------------------------------------------------//

#------[File descibe]-------#

[Preprocessed code]：contain three python files, for some featrues processing and data processing.

[Testing code]：Contain four folders, version 2 obtain better scrore.
	        Each folders contains two python files for loading testing datasets and fitting to get predictions.
		Models used here are contain in Training model.rar, see detailed info below

[Training code]：Contain two python files.
		 One is for training model flow (model algorithm can choose: Random Forest, XGBoost)
		 the other one is score calculating function based on the calculate method provided by official to calculate the score of this model. 

[Training model]：models use in every versions. PLease unzip them first.
		 RFC_only.pkl used in version1 & version4
		 XGB_only.pkl used in version2 & version4
		 XGB_whole_01.pkl~05 are uesd in version5
		 

#------[File Note]-------#
Due to the license agreement signed with official, so i won't update either training datasets or testing datasets.


###------important------###
If there's ant problem, please contact me:
e-mail：shaowen.eic09g@nctu.nctu.edu
