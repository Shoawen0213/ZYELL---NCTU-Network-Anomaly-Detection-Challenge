#!/usr/bin/env python
# coding: utf-8

# In[61]:


import os
import glob
import sys
import time
import random
import numpy as np
import pandas as pd
import socket
import struct
import datacompy
from tqdm.notebook import tqdm
from sklearn.model_selection import GridSearchCV
from sklearn import metrics
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split

from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib

from xgboost import XGBClassifier


# In[18]:


print("now in...")
now_path = os.getcwd()
# file_path = os.getcwd()+ '/testing_dataset'
print(now_path)


# In[19]:


# orginal dataframe (66 features)
org_list = ['int_time', 'int_src', 'int_dst', 'spt', 'dpt', 'duration',
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
org_df = pd.DataFrame(columns = ['int_time', 'int_src', 'int_dst', 'spt', 'dpt', 'duration',
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
org_df # 0 rows × 66 columns


# In[20]:


file_path = './Time&&IP_in_int(26col).csv'
train_data = pd.read_csv(file_path)
train_data     #9241463 rows × 26 columns


# In[21]:


unique, counts = np.unique(train_data['label'], return_counts=True)
print("xgbc_predict contains:{}".format(dict(zip(unique, counts))))


# In[22]:


train_Normal = train_data.loc[train_data['label'].str.contains('Normal')]
print("Total numbers of Normal : {}".format(len(train_Normal)))

train_Normal


# In[44]:


train_DOS_smurf = train_data.loc[train_data['label'].str.contains('DOS-smurf')]
print("Total numbers of DOS-smurf : {}".format(len(train_DOS_smurf)))

train_Probing_Ipsweep = train_data.loc[train_data['label'].str.contains('Probing-IP sweep')]
print("Total numbers of Probing-Ipsweep : {}".format(len(train_Probing_Ipsweep)))

train_Probing_Nmap = train_data.loc[train_data['label'].str.contains('Probing-Nmap')]
print("Total numbers of Probing-Nmap : {}".format(len(train_Probing_Nmap)))

train_Probing_Port_sweep = train_data.loc[train_data['label'].str.contains('Probing-Port sweep')]
print("Total numbers of Probing-Port sweep : {}".format(len(train_Probing_Port_sweep)))

concat_Malicious = pd.concat([train_DOS_smurf, train_Probing_Ipsweep, train_Probing_Nmap, train_Probing_Port_sweep], axis=0)

concat_Malicious.index = range(len(concat_Malicious))


# In[45]:


print(len(concat_Malicious))


# In[46]:


def re_build_train(slice_num, train_Normal_orgi, train_Malicious_orgi):
    rand_seed = random.randint(0, 300)
    print("Random seed in this time is :", rand_seed)
    train_Normal_rand = train_Normal_orgi.sample(n=slice_num, random_state=rand_seed, axis=0)
    print("length of new random Normal data:", len(train_Normal_rand))
    
    rand_seed_m = random.randint(0, 500)
    print("rand_seed_m in this time is :", rand_seed_m)
    
    train_Malicious_rand = train_Malicious_orgi.sample(n=slice_num, random_state=rand_seed_m, axis=0)
    
    concat_train_data = pd.concat([train_Normal_rand, train_Malicious_rand], axis=0)
    print("New length of new training data:", len(concat_train_data))
                                   
    concat_train_data.index = range(len(concat_train_data))
    print("Finish building new index")
                                   
    return concat_train_data

def data_transform_for_fit(dataframe, org_list,  org_df):
    # use dummy on "app"
    dataframe_dum_app = dataframe.join(pd.get_dummies(dataframe.app))
    print("shape of dataframe after dummy:{}".format(dataframe_dum_app.shape)) 
    
    #delete ['time', 'src', 'dst', 'app']
    dataframe_dum_app = dataframe_dum_app.drop(columns = ['time', 'src', 'dst', 'app'])

    print("Start to check lost app feature...")
    compare = datacompy.Compare(dataframe_dum_app, org_df, on_index = True)
    print("compare Result:", compare.report())
    print("//----------------------------------------------//")
    print("缺少的為 :{}".format(compare.df2_unq_columns()))
    lost_list = compare.df2_unq_columns()
    
    lost_zero = np.zeros([len(dataframe_dum_app) , len(lost_list)]) 
    concact_lost_zero_df = pd.DataFrame(lost_zero, columns = lost_list)
    print("shape of concact_lost_zero_df:{}".format(concact_lost_zero_df.shape)) 
    print("//----------------------------------------------//")
    dataframe_66col =  pd.concat([dataframe_dum_app, concact_lost_zero_df], axis=1)
    print("shape of dataframe_66col:{}".format(dataframe_66col.shape))
    print("//----------------------------------------------//")
    
    print("Check if there's any missing...")
    dataframe_66col_reload = dataframe_66col[org_list]
    compare = datacompy.Compare(dataframe_66col, dataframe_66col_reload, on_index = True)
    print("compare Result:", compare.report())
    print("缺少的為 :{}".format(compare.df2_unq_columns()))
    if compare.df2_unq_columns() == str(set()):
        print("There;s just completely the same.")
    else :
        print("{} is missing".format(compare.df2_unq_columns()))
    print("//----------------------------------------------//")
    
    return dataframe_66col

def data_process_for_fit(dataframe):
    random_state = random.randint(0, 500)
    
    x = dataframe[['int_time', 'int_src', 'int_dst', 'spt', 'dpt', 'duration',
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
       'tftp', 'vdolive']] 
    y = dataframe[['label']]
    
    #split data
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=random_state)
    
    '''
          Argument:
            'Normal'             --> 1
            'Probing-Nmap'       --> 3
            'Probing-Port sweep' --> 4
            'Probing-IP sweep'   --> 2
            'DDOS-smurf'         --> 0
    '''

    label_list = ['Normal', 'DOS-smurf', 'Probing-Ipsweep', 'Probing-Nmap', 'Probing-Port sweep']
    print("label_list : {}".format(label_list))
    print("//--------------------------------------------//")

    #label encode
    labelencoder = LabelEncoder()
    y_train_LE = labelencoder.fit_transform(y_train)
    print("y_train labeled after label encode : {}".format(y_train_LE))

    print("shape of y_train data : ", y_train_LE.shape)
    unique, counts = np.unique(y, return_counts=True)
    print("y_train data contains:{} ".format(dict(zip(unique, counts))))

    print("//--------------------------------------------//")

    y_test_LE = labelencoder.fit_transform(y_test)
    print("y_test labeled after label encode : {}".format(y_test_LE))

    print("shape of y_train_LE data : ", y_test_LE.shape)
    unique, counts = np.unique(y_test_LE, return_counts=True)
    print("y_test_LE data contains:{} ".format(dict(zip(unique, counts))))
    
    print("x_train shape is: {}".format(x_train.shape))
    print("x_test shape  is: {}".format(x_test.shape))
    print("y_train_LE shape is: {}".format(y_train_LE.shape))
    print("y_test_LE shape  is: {}".format(y_test_LE.shape))
    
    return x_train, x_test, y_train_LE, y_test_LE
    
    


def valid_modell(model, x_test, y_test):
    _predict = model.predict(x_test)
    print("shape of _predict : ", _predict.shape)
    unique, counts = np.unique(_predict, return_counts=True)
    print("_predict contains:{}".format(dict(zip(unique, counts))))

    print('The accuracy on testing data set', model.score(x_test, y_test))

    #run score(define by shao_pun)
    get_ipython().run_line_magic('run', 'score.py')

    #transform into numpy array
    y_array = np.array(y_test)
    _pred_array = np.array(_predict).reshape(len(_predict), 1)

    score_ = score(_pred_array, y_array)
    print('The score that calculated by SP version of XGBClassifier on testing data set', score_)


# In[48]:


slice_num = 250000
rand_train = re_build_train(slice_num, train_Normal, concat_Malicious)
rand_train #720986 rows × 26 columns


# In[ ]:


slice_num = 400000
rand_train = re_build_train(slice_num, train_Normal, train_DOS_smurf, train_Probing_Ipsweep, train_Probing_Nmap, train_Probing_Port_sweep)
rand_train #720986 rows × 26 columns


# In[ ]:


data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #720986 rows × 67 columns


# In[ ]:


x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)


# In[41]:


# use Random Forest Classifier (parameter tune ver1)
from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    n_estimators=80,
    max_depth=25,
    max_features='sqrt',
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)


# In[42]:


#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver1.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver1.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[27]:


# use Random Forest Classifier (parameter tune ver2)
slice_num = 400000
rand_train = re_build_train(slice_num, train_Normal, train_DOS_smurf, train_Probing_Ipsweep, train_Probing_Nmap, train_Probing_Port_sweep)
rand_train #720986 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #720986 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    n_estimators=100,
    max_depth=30,
    max_features='sqrt',
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver2.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver2.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[28]:


# use Random Forest Classifier (parameter tune ver3)
slice_num = 400000
rand_train = re_build_train(slice_num, train_Normal, train_DOS_smurf, train_Probing_Ipsweep, train_Probing_Nmap, train_Probing_Port_sweep)
rand_train #720986 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #720986 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    n_estimators=105,
    max_depth=25,
    max_features='sqrt',
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver3.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver3.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[29]:


# use Random Forest Classifier (parameter tune ver4)
slice_num = 400000
rand_train = re_build_train(slice_num, train_Normal, train_DOS_smurf, train_Probing_Ipsweep, train_Probing_Nmap, train_Probing_Port_sweep)
rand_train #720986 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #720986 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    n_estimators=110,
    max_depth=35,
    max_features='sqrt',
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver4.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver4.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[34]:


# use Random Forest Classifier (parameter tune ver5)
slice_num = 400000
rand_train = re_build_train(slice_num, train_Normal, train_DOS_smurf, train_Probing_Ipsweep, train_Probing_Nmap, train_Probing_Port_sweep)
rand_train #720986 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #720986 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    n_estimators=150,
    max_depth=35,
    max_features='sqrt',
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver5.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver5.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[35]:


# use Random Forest Classifier (parameter tune ver6)
slice_num = 400000
rand_train = re_build_train(slice_num, train_Normal, train_DOS_smurf, train_Probing_Ipsweep, train_Probing_Nmap, train_Probing_Port_sweep)
rand_train #720986 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #720986 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    n_estimators=200,
    max_depth=50,
    max_features='sqrt',
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver6.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver6.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[36]:


# use Random Forest Classifier (parameter tune ver7)
slice_num = 400000
rand_train = re_build_train(slice_num, train_Normal, train_DOS_smurf, train_Probing_Ipsweep, train_Probing_Nmap, train_Probing_Port_sweep)
rand_train #720986 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #720986 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    n_estimators=155,
    max_depth=40,
    max_features='sqrt',
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver7.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver7.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[37]:


# use Random Forest Classifier (parameter tune ver8)
slice_num = 400000
rand_train = re_build_train(slice_num, train_Normal, train_DOS_smurf, train_Probing_Ipsweep, train_Probing_Nmap, train_Probing_Port_sweep)
rand_train #720986 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #720986 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    n_estimators=155,
    max_depth=40,
    max_features='log2',
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver8.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver8.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[38]:


# use Random Forest Classifier (parameter tune ver9)
slice_num = 400000
rand_train = re_build_train(slice_num, train_Normal, train_DOS_smurf, train_Probing_Ipsweep, train_Probing_Nmap, train_Probing_Port_sweep)
rand_train #720986 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #720986 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    n_estimators=180,
    max_depth=45,
    max_features='log2',
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver9.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver9.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[39]:


# use Random Forest Classifier (parameter tune ver10)
slice_num = 400000
rand_train = re_build_train(slice_num, train_Normal, train_DOS_smurf, train_Probing_Ipsweep, train_Probing_Nmap, train_Probing_Port_sweep)
rand_train #720986 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #720986 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    n_estimators=185,
    max_depth=40,
    max_features='sqrt',
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver10.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver10.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[40]:


# use Random Forest Classifier (parameter tune ver0
slice_num = 400000
rand_train = re_build_train(slice_num, train_Normal, train_DOS_smurf, train_Probing_Ipsweep, train_Probing_Nmap, train_Probing_Port_sweep)
rand_train #720986 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #720986 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver0.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0305_tune_para_slice_normal_ver0.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[ ]:





# In[ ]:





# In[49]:


slice_num = 250000
rand_train = re_build_train(slice_num, train_Normal, concat_Malicious)
rand_train #500000 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #500000 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0306_slice_all_ver0.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0306_slice_all_ver0.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[52]:


slice_num = 200000
rand_train = re_build_train(slice_num, train_Normal, concat_Malicious)
rand_train #500000 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #500000 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0306_slice_all_ver1.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0306_slice_all_ver1.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[53]:


slice_num = 230000
rand_train = re_build_train(slice_num, train_Normal, concat_Malicious)
rand_train #500000 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #500000 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0306_slice_all_ver2.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0306_slice_all_ver2.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[54]:


slice_num = 234568
rand_train = re_build_train(slice_num, train_Normal, concat_Malicious)
rand_train #500000 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #500000 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0306_slice_all_ver3.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0306_slice_all_ver3.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[56]:


slice_num = 244444
rand_train = re_build_train(slice_num, train_Normal, concat_Malicious)
rand_train #500000 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #500000 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0306_slice_all_ver4.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0306_slice_all_ver4.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[58]:


slice_num = 236541
rand_train = re_build_train(slice_num, train_Normal, concat_Malicious)
rand_train #500000 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #500000 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0306_slice_all_ver5.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0306_slice_all_ver5.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[59]:


slice_num = 198563
rand_train = re_build_train(slice_num, train_Normal, concat_Malicious)
rand_train #500000 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #500000 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0306_slice_all_ver6.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0306_slice_all_ver6.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[60]:


slice_num = 201658
rand_train = re_build_train(slice_num, train_Normal, concat_Malicious)
rand_train #500000 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #500000 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(
    verbose=1,
    n_jobs=-1
    )
rfc.fit(x_train, y_train_LE)

#save model
joblib.dump(rfc, "/home/shaowen0213/NAD/testing_set/Save Model/rfc_0306_slice_all_ver7.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/rfc_0306_slice_all_ver7.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[ ]:





# In[ ]:





# In[62]:


slice_num = 250000
rand_train = re_build_train(slice_num, train_Normal, concat_Malicious)
rand_train #500000 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #500000 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

xgbc = XGBClassifier(
    verbose=1,
    n_jobs=-1
)

xgbc.fit(x_train, y_train_LE)

#save model
joblib.dump(xgbc, "/home/shaowen0213/NAD/testing_set/Save Model/xgb_0306_slice_all_ver0.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/xgb_0306_slice_all_ver0.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[63]:


slice_num = 220000
rand_train = re_build_train(slice_num, train_Normal, concat_Malicious)
rand_train #500000 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #500000 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

xgbc = XGBClassifier(
    verbose=1,
    n_jobs=-1
)

xgbc.fit(x_train, y_train_LE)

#save model
joblib.dump(xgbc, "/home/shaowen0213/NAD/testing_set/Save Model/xgb_0306_slice_all_ver1.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/xgb_0306_slice_all_ver1.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[64]:


slice_num = 201654
rand_train = re_build_train(slice_num, train_Normal, concat_Malicious)
rand_train #500000 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #500000 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

xgbc = XGBClassifier(
    verbose=1,
    n_jobs=-1
)

xgbc.fit(x_train, y_train_LE)

#save model
joblib.dump(xgbc, "/home/shaowen0213/NAD/testing_set/Save Model/xgb_0306_slice_all_ver2.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/xgb_0306_slice_all_ver2.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[65]:


slice_num = 200000
rand_train = re_build_train(slice_num, train_Normal, concat_Malicious)
rand_train #500000 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #500000 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

xgbc = XGBClassifier(
    verbose=1,
    n_jobs=-1
)

xgbc.fit(x_train, y_train_LE)

#save model
joblib.dump(xgbc, "/home/shaowen0213/NAD/testing_set/Save Model/xgb_0306_slice_all_ver3.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/xgb_0306_slice_all_ver3.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[66]:


slice_num = 201652
rand_train = re_build_train(slice_num, train_Normal, concat_Malicious)
rand_train #500000 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #500000 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

xgbc = XGBClassifier(
    verbose=1,
    n_jobs=-1
)

xgbc.fit(x_train, y_train_LE)

#save model
joblib.dump(xgbc, "/home/shaowen0213/NAD/testing_set/Save Model/xgb_0306_slice_all_ver4.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/xgb_0306_slice_all_ver4.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[68]:


slice_num = 186952
rand_train = re_build_train(slice_num, train_Normal, concat_Malicious)
rand_train #500000 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #500000 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

xgbc = XGBClassifier(
    verbose=1,
    n_jobs=-1
)

xgbc.fit(x_train, y_train_LE)

#save model
joblib.dump(xgbc, "/home/shaowen0213/NAD/testing_set/Save Model/xgb_0306_slice_all_ver5.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/xgb_0306_slice_all_ver5.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[69]:


slice_num = 203659
rand_train = re_build_train(slice_num, train_Normal, concat_Malicious)
rand_train #500000 rows × 26 columns

data_transform = data_transform_for_fit(rand_train, org_list,  org_df)
data_transform #500000 rows × 67 columns

x_train, x_test, y_train_LE, y_test_LE = data_process_for_fit(data_transform)

xgbc = XGBClassifier(
    verbose=1,
    n_jobs=-1
)

xgbc.fit(x_train, y_train_LE)

#save model
joblib.dump(xgbc, "/home/shaowen0213/NAD/testing_set/Save Model/xgb_0306_slice_all_ver6.pkl")


#load model
model = joblib.load('/home/shaowen0213/NAD/testing_set/Save Model/xgb_0306_slice_all_ver6.pkl')

print('The accuracy of Random Forest Classifier on testing data set', model.score(x_test, y_test_LE))

valid_modell(model, x_test, y_test_LE)


# In[ ]:





# In[ ]:




