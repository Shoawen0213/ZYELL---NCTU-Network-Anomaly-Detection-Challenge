#!/usr/bin/env python
# coding: utf-8

import os
import glob
import sys
import time
import numpy as np
import pandas as pd
import datacompy
import csv
from time import sleep
from random import uniform
from tqdm import tqdm
from scipy import stats 
from pandas import  DataFrame
from tqdm.notebook import tqdm

from sklearn.externals import joblib
from sklearn.preprocessing import LabelEncoder

print("Loading model...")
m=0
n=0
#load model
model1 = joblib.load('./rfc1_for_ver8.pkl')
m+=1
model2 = joblib.load('./rfc2_for_ver8.pkl')
m+=1
model3 = joblib.load('./rfc3_for_ver8.pkl')
m+=1

model4 = joblib.load('./xgbc1_for_ver8.pkl')
n+=1
model5 = joblib.load('./xgbc2_for_ver8.pkl')
n+=1
model6 = joblib.load('./xgbc3_for_ver8.pkl')
n+=1
model7 = joblib.load('./xgbc4_for_ver8.pkl')
n+=1

print("Finisg loading...")
print("We got {} sub-model".format(m+n))
print("contain {} 's RFC and {}'s XGB.".format(m, n))


# orginal dataframe (64 features)
org_list = [ 'spt', 'dpt', 'duration',
       'out (bytes)', 'in (bytes)', 'proto', 'cnt_dst', 'cnt_src',
       'cnt_serv_src', 'cnt_serv_dst', 'cnt_dst_slow', 'cnt_src_slow',
       'cnt_serv_src_slow', 'cnt_serv_dst_slow', 'cnt_dst_conn',
       'cnt_src_conn', 'cnt_serv_src_conn', 'cnt_serv_dst_conn',
       'aim', 'auth', 'bgp', 'bootpc', 'bootps', 'domain', 'finger', 'ftp',
       'h323', 'http', 'https', 'icmp', 'icq', 'igmp', 'irc', 'isakmp',
       'microsoft-ds', 'msn', 'netbios-dgm', 'netbios-ns', 'netbios-ssn',
       'news', 'nfs', 'nntp', 'others', 'pop3', 'pptp', 'rcmd', 'real-audio',
       'rexec', 'rlogin', 'roadrunner', 'rtsp', 'sftp', 'smtp', 'snmp',
       'snmp-trap', 'sql-net', 'ssdp', 'ssh', 'syslog', 'tacacs', 'telnet',
       'tftp', 'vdolive']
org_df = pd.DataFrame(columns = [ 'spt', 'dpt', 'duration',
       'out (bytes)', 'in (bytes)', 'proto', 'cnt_dst', 'cnt_src',
       'cnt_serv_src', 'cnt_serv_dst', 'cnt_dst_slow', 'cnt_src_slow',
       'cnt_serv_src_slow', 'cnt_serv_dst_slow', 'cnt_dst_conn',
       'cnt_src_conn', 'cnt_serv_src_conn', 'cnt_serv_dst_conn',
       'aim', 'auth', 'bgp', 'bootpc', 'bootps', 'domain', 'finger', 'ftp',
       'h323', 'http', 'https', 'icmp', 'icq', 'igmp', 'irc', 'isakmp',
       'microsoft-ds', 'msn', 'netbios-dgm', 'netbios-ns', 'netbios-ssn',
       'news', 'nfs', 'nntp', 'others', 'pop3', 'pptp', 'rcmd', 'real-audio',
       'rexec', 'rlogin', 'roadrunner', 'rtsp', 'sftp', 'smtp', 'snmp',
       'snmp-trap', 'sql-net', 'ssdp', 'ssh', 'syslog', 'tacacs', 'telnet',
       'tftp', 'vdolive'])


def main(dataframe):
    print('//---------------------//')
    print("// now using model1... //")
    print('//---------------------//')
    model1_pred_prob = fit_data_dum(dataframe, org_list,  org_df, model1)
    model1_pred_prob_df = pd.DataFrame(model1_pred_prob)
    del model1_pred_prob
    
    print('//---------------------//')
    print("// now using model2... //")
    print('//---------------------//')
    model2_pred_prob = fit_data_dum(dataframe, org_list,  org_df, model2)
    model2_pred_prob_df = pd.DataFrame(model2_pred_prob)
    del model2_pred_prob
   
    print('//---------------------//')
    print("// now using model3... //")
    print('//---------------------//')
    model3_pred_prob = fit_data_dum(dataframe, org_list,  org_df, model3)
    model3_pred_prob_df = pd.DataFrame(model3_pred_prob)
    del model3_pred_prob

    print('//---------------------//')
    print("// now using model4... //")
    print('//---------------------//')
    model4_pred_prob = fit_data_dum(dataframe, org_list,  org_df, model4)
    model4_pred_prob_df = pd.DataFrame(model4_pred_prob)
    del model4_pred_prob
     
    print('//---------------------//')
    print("// now using model5... //")
    print('//---------------------//')
    model5_pred_prob = fit_data_dum(dataframe, org_list,  org_df, model5)
    model5_pred_prob_df = pd.DataFrame(model5_pred_prob)
    del model5_pred_prob
     
     
    print('//---------------------//')
    print("// now using model6... //")
    print('//---------------------//')
    model6_pred_prob = fit_data_dum(dataframe, org_list,  org_df, model6)
    model6_pred_prob_df = pd.DataFrame(model6_pred_prob)
    del model6_pred_prob
     
    
    print('//---------------------//')
    print("// now using model7... //")
    print('//---------------------//')
    model7_pred_prob = fit_data_dum(dataframe, org_list,  org_df, model7)
    model7_pred_prob_df = pd.DataFrame(model7_pred_prob)
    del model7_pred_prob
    
    print('//-------------------------//')
    print("// concat all predict data //")
    print('//-------------------------//')  
    concat_pred_prob_df = pd.concat([model1_pred_prob_df, model2_pred_prob_df, model3_pred_prob_df, model4_pred_prob_df, model5_pred_prob_df,
                                    model6_pred_prob_df, model7_pred_prob_df], axis=1)
    
    del model1_pred_prob_df, model2_pred_prob_df, model3_pred_prob_df, model4_pred_prob_df, model5_pred_prob_df
    del model6_pred_prob_df, model7_pred_prob_df

    return concat_pred_prob_df


def fit_data_dum(dataframe, org_list, org_df, model):
    dataframe_dum = dataframe.join(pd.get_dummies(dataframe.app))
    dataframe_dum = dataframe_dum.drop(columns = ['time', 'int_time', 'src', 'int_src', 'dst', 'int_dst', 'app'])
    print("shape of dataframe_dum is :", dataframe_dum.shape)
    print("//----------------------------------------------//")

    print("Start to check lost app feature...")
    compare = datacompy.Compare(dataframe_dum, org_df, on_index = True)
    print("compare Result --> lost :", compare.df2_unq_columns())
    print("//----------------------------------------------//")
    lost_list = compare.df2_unq_columns()
    
    lost_zero = np.zeros([len(dataframe_dum) , len(lost_list)]) 
    concact_lost_zero_df = pd.DataFrame(lost_zero, columns = lost_list)
    del lost_zero
    del lost_list
    
    print("shape of concact_lost_zero_df:{}".format(concact_lost_zero_df.shape)) 
    print("//----------------------------------------------//")
    dataframe_col =  pd.concat([dataframe_dum, concact_lost_zero_df], axis=1)
    print("shape of dataframe_col:{}".format(dataframe_col.shape))
    print("//----------------------------------------------//")
    
    print("Check if there's any missing...")
    dataframe_col_reload = dataframe_col[org_list]
    compare = datacompy.Compare(dataframe_col, dataframe_col_reload, on_index = True)
    
    del dataframe_col
    
    print("compare Result:", compare.report())
    print("//----------------------------------------------//")
    
    print("Start to PREDICT!...")
    model_pred_prob = model.predict_proba(dataframe_col_reload)
    print("predict result : ", model_pred_prob)
    print("--------------------------------")
    print("shape of predict data : ", model_pred_prob.shape)
    del dataframe_col_reload
    
    return model_pred_prob
    

def dum_inverse(df):
    label_list = ['Normal', 'DDOS-smurf', 'Probing-IP sweep', 'Probing-Nmap', 'Probing-Port sweep']
    print("label_list : {}".format(label_list))
    #label encode
    labelencoder = LabelEncoder()
    y = labelencoder.fit_transform(label_list)
    print("label_list after label encode : {}".format(y))
    print("//--------------------------------------------//")
    del y 
    
    #label encode revise
    transform = labelencoder.inverse_transform(df)
    df_inverse = pd.DataFrame(transform, columns = ['label'])
    print("Label revised : {}".format(df_inverse))
    print("shape of revised label : ", df_inverse.shape)
    unique, counts = np.unique(df_inverse, return_counts=True)
    print("xgbc_predict contains:{}".format(dict(zip(unique, counts))))
    
    del transform
    
    return df_inverse

def concat(dataframe, concat_df):
    dataframe_orgi = dataframe.drop(columns = ['int_time', 'int_src', 'int_dst'])
    print("//--------------------------------------------//")
    print("shape of orginal data : ", dataframe_orgi.shape)
    
    print("//--------------------------------------------//")
    data_concat =  pd.concat([dataframe_orgi, concat_df], axis=1)
    print("shape of data_concat : ", data_concat.shape)
    
    del dataframe_orgi
   
    return data_concat
    
print("//********************************//")
print("//    Loading stage 2 model...    //")
print("//********************************//")

model_s2 = joblib.load('./final_stage_rf_clfver_4XGB.pkl')

print(" Loading model Successes! ")

# prediction for test_0123
print("//*******************************************//")
print("//*      Now predict for test data 0123     *//")
print("//*               Now using...              *//")
print("//*    3RFC + 4XGB + RandomForestClassifier *//")
print("//*******************************************//")
file_path = './transformed/0123_transformed_solo.csv'
test_data_0123 = pd.read_csv(file_path)

pred_prob_0123 = main(test_data_0123)

print("------------------------------------------------")

_predict = model_s2.predict(pred_prob_0123)
print("shape of _predict : ", _predict.shape)
unique, counts = np.unique(_predict, return_counts=True)
print("_predict contains:{}".format(dict(zip(unique, counts))))

print("------------------------------------------------")
print("//    Now doing label encode inverse    //")

_predict_inverse = dum_inverse(_predict)
print("shape of _predict_inverse : ", _predict_inverse.shape)
unique, counts = np.unique(_predict_inverse, return_counts=True)
print("_predict_inverse contains:{}".format(dict(zip(unique, counts))))

del _predict
print("------------------------------------------------")
concat_data = concat(test_data_0123, _predict_inverse)
print("shape of concat_data" , concat_data.shape)

print("//    Now Store the result    //")
#store to csv files 
concat_data.to_csv('./131_OASIS LAB_08_0123_firewall.csv', index=False, encoding='utf-8-sig')

del _predict_inverse
del concat_data
del test_data_0123

print(" 0123 Finish!")

# prediction for test_0124
print("//*******************************************//")
print("//*      Now predict for test data 0124     *//")
print("//*               Now using...              *//")
print("//*    3RFC + 4XGB + RandomForestClassifier *//")
print("//*******************************************//")
file_path = './transformed/0124_transformed_solo.csv'
test_data_0124 = pd.read_csv(file_path)

pred_prob_0124 = main(test_data_0124)

_predict = model_s2.predict(pred_prob_0124)
print("shape of _predict : ", _predict.shape)
unique, counts = np.unique(_predict, return_counts=True)
print("_predict contains:{}".format(dict(zip(unique, counts))))
print("------------------------------------------------")
print("//    Now doing label encode inverse    //")

_predict_inverse = dum_inverse(_predict)
print("shape of _predict_inverse : ", _predict_inverse.shape)
unique, counts = np.unique(_predict_inverse, return_counts=True)
print("_predict_inverse contains:{}".format(dict(zip(unique, counts))))

del _predict
print("------------------------------------------------")
concat_data = concat(test_data_0124, _predict_inverse)
print("shape of concat_data" , concat_data.shape)

print("//    Now Store the result    //")
#store to csv files 
concat_data.to_csv('./131_OASIS LAB_08_0124_firewall.csv', index=False, encoding='utf-8-sig')

del _predict_inverse
del concat_data
del test_data_0124

print(" 0124 Finish!")

# prediction for test_0125
print("//*******************************************//")
print("//*      Now predict for test data 0125     *//")
print("//*               Now using...              *//")
print("//*    3RFC + 4XGB + RandomForestClassifier *//")
print("//*******************************************//")
file_path = './transformed/0125_transformed_solo.csv'
test_data_0125 = pd.read_csv(file_path)

pred_prob_0125 = main(test_data_0125)

_predict = model_s2.predict(pred_prob_0125)
print("shape of _predict : ", _predict.shape)
unique, counts = np.unique(_predict, return_counts=True)
print("_predict contains:{}".format(dict(zip(unique, counts))))
print("------------------------------------------------")
print("//    Now doing label encode inverse    //")
_predict_inverse = dum_inverse(_predict)
print("shape of _predict_inverse : ", _predict_inverse.shape)
unique, counts = np.unique(_predict_inverse, return_counts=True)
print("_predict_inverse contains:{}".format(dict(zip(unique, counts))))

del _predict
print("------------------------------------------------")
concat_data = concat(test_data_0125, _predict_inverse)
print("shape of concat_data" , concat_data.shape)

print("//    Now Store the result    //")
#store to csv files 
concat_data.to_csv('./131_OASIS LAB_08_0125_firewall.csv', index=False, encoding='utf-8-sig')

del _predict_inverse
del concat_data
del test_data_0125

print(" 0125 Finish!")


# prediction for test_0126
print("//*******************************************//")
print("//*      Now predict for test data 0126     *//")
print("//*               Now using...              *//")
print("//*    3RFC + 4XGB + RandomForestClassifier *//")
print("//*******************************************//")
file_path = './transformed/0126_transformed_solo.csv'
test_data_0126 = pd.read_csv(file_path)

pred_prob_0126 = main(test_data_0126)

_predict = model_s2.predict(pred_prob_0126)
print("shape of _predict : ", _predict.shape)
unique, counts = np.unique(_predict, return_counts=True)
print("_predict contains:{}".format(dict(zip(unique, counts))))
print("------------------------------------------------")
print("//    Now doing label encode inverse    //")
_predict_inverse = dum_inverse(_predict)
print("shape of _predict_inverse : ", _predict_inverse.shape)
unique, counts = np.unique(_predict_inverse, return_counts=True)
print("_predict_inverse contains:{}".format(dict(zip(unique, counts))))

del _predict

concat_data = concat(test_data_0126, _predict_inverse)
print("shape of concat_data" , concat_data.shape)
print("------------------------------------------------")
print("//    Now Store the result    //")
#store to csv files 
concat_data.to_csv('./131_OASIS LAB_08_0126_firewall.csv', index=False, encoding='utf-8-sig')

del _predict_inverse
del concat_data
del test_data_0126
del model1, model2, model3, model4, model5, model6, model7 

print(" 0126 Finish!")
