import requests
from bs4 import BeautifulSoup
import urllib.request
import numpy as np
from collections import defaultdict
import simplejson as json
import collections
import pandas as pd
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
import random
import glob
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import io
import gzip
import random
import os
import itertools
import pathlib
import re
from scipy import sparse
from sklearn import svm
from sklearn.svm import LinearSVC
from scipy.stats import uniform
from tqdm import tqdm


'''
A method that gets all immediate subdirectories of the path passed in;
The key in the dict is the catagory of app and value is the app name.
This will give a list of all the apps for a given catagory

path - the path of the directory used to obtain the apps (specified in main/config)
'''
def catagoryApps(path):

    #get immediate subdirectories of PATH
    list_subfolders_with_paths = [f.path for f in os.scandir(path) if f.is_dir()]

    directDic = {}

    for direct in list_subfolders_with_paths:
        subdirs = []
        for sub in os.scandir(direct):
            if sub.is_dir():
                subdirs.append(sub.name)
        directDic[direct.split("/")[-1]] = subdirs

    return directDic


'''
A method to count the benign apps which will help in getting the same amount
of malware apps to maintain a balanced dataset 

dic - the list of directories containing their apps 
'''
def countBenign(dic):
    List_flat = list(itertools.chain(*dic.values()))
    return len(List_flat)

'''
A method that will get the malware apps from their designated location
'''
def malware_app_paths():
    malware_loc = []
    dir_list = os.listdir("/datasets/dsc180a-wi20-public/Malware/amd_data_smali")
    for i in dir_list:
        string = '/datasets/dsc180a-wi20-public/Malware/amd_data_smali/' + i
        lis = os.listdir(string)
        for variety in lis:
            new_string = string + '/' + variety
            app_list = os.listdir(new_string)
            for app in app_list:
                final_str = new_string + '/' + app
                malware_loc.append(final_str)
    return malware_loc
#---------------------------------------------Data Structure Creation----------------------------------------------------------#
'''
A helper function that helps extracted the API calls and Packages for the data structure
used for Invoke_Types, All_APIs, and Packages.
**This function was created based on feedback recieved in Assignment 2**

catagory - the catagory of an app

appName - the name of the app

line - the line being read in from the smali file

methodIDCount - a unique method id (key) that will be assigned as a key to represent a list
of methods (value) in the data strucutre

catDict - The data structure being created

invokeType - The invoke type a method is invoked with
'''
def dataStructureHelper(catagory, appName, line, methodIDCount, catDict, invokeType):
    patAPI = re.compile('^[^}]*}')
    patPack = re.compile('^(.*?)->')
    parChar = re.compile('[^(]*')

    methodID = 'method_' + str(methodIDCount)
    result = re.sub(patAPI, '', str(line))
    apiCall = result[2:]
    apiNoParam = re.match(parChar, apiCall)


    apiCall = apiNoParam.group(0) + str('()')
    package = re.search(patPack, apiCall)

    catDict[catagory][appName]['Packages'][package.group(1)].append(apiCall)
    catDict[catagory][appName]['All_APIs']['APIs'].append(apiCall)

    #Not using invoke types for Kernel (I-Matrix and invoke types Work properly)
    #catDict[catagory][appName]['Invoke_Type'][invokeType].append(apiCall)

    catDict[catagory][appName]['Methods'][methodID].append(apiCall)


'''
A helper function that helps create the values for Invoke_Types, All_APIs, and Packages.
**This function was created based on feedback recieved in Assignment 2**

catDict - The data structure being created

catagory - the catagory of an app

appName - the name of the app
'''
def getUniqueAPIs(catDict, catagory, appName):

    #get the set of all APIs for an app with the same invoke type and put them into a list
    #invokeTypes = ['invoke-static', 'invoke-virtual', 'invoke-direct', 'invoke-super', 'invoke-interface']
    
        #for invoke in invokeTypes:
            #catDict[catagory][appName]['Invoke_Type'][invoke] = list(set(catDict[catagory][appName]['Invoke_Type'][invoke]))

        #get the set of all APIs for an app that are called in the application
        catDict[catagory][appName]['All_APIs']['APIs'] = list(set(catDict[catagory][appName]['All_APIs']['APIs']))

        #get the set of all packages in an app that are used in an application
        for pack in catDict[catagory][appName]['Packages']:
            catDict[catagory][appName]['Packages'][pack] = list(set(catDict[catagory][appName]['Packages'][pack]))



'''
A method that creates a json object of the data structure used for creating the matricies.
The datastructure is comprised of nested dictionaries (see catDict variable). A catagory is a
key for a dictionary of app names. App names are keys for Packages, All_APIs, Invoke_Type, and
Methods. Packages contains all the unique packages used in that app. All_APIs contains a list
of all unique api calls made in that app. Invoke_Type is the key with 5 coresponding invoke types
as the values which contain a list of all the APIs that are invoked the smae way. Methods contains
lists of methods in the same code block with each list having a unique method id as a key and the
list of methods occuring in the same code block as the value. For more information
on how this data structure is created please see report.

path - the path of the directory used to obtain the apps (specified in main/config)

'''

def createDataStructure(path):

    catDict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))


    methodIDCount = 0
    methodList = []
    inMethod = False
    methodID = 'method_' + str(methodIDCount)


    startMethod = '.method'
    endMethod = '.end method'

    directDic = catagoryApps(path)
    numMal = countBenign(directDic)
    print("Loading Begin Apps into Data Structure....")

    for catagory in directDic:

        for appName in tqdm(directDic[catagory]):
            #get path of appname in dir
            newPath = path + str(catagory) + '/' + str(appName) + '/' + 'smali'
            if os.path.isdir(newPath):
                #go into smali file and get all the .methods and .endmethods using regex
                #assign unique id for each method (key) which will have a list of API calls for the values
                samliFiles = glob.glob(newPath + '/**/*.smali', recursive=True)
                #read each smali file and get the method calls
                for file in samliFiles:
                    f = open(file, "r")
                    Lines = f.readlines()
                    for line in Lines:
                        if startMethod in line:
                            inMethod = True

                        if inMethod and (endMethod in line):
                            inMethod = False
                            methodIDCount += 1
                            methodList = []

                        if (inMethod) and ('invoke-static' in line):
                            invokeType = 'invoke-static'
                            dataStructureHelper(catagory, appName, line, methodIDCount, catDict, invokeType)

                        if (inMethod) and ('invoke-virtual' in line):
                            invokeType = 'invoke-virtual'
                            dataStructureHelper(catagory, appName, line, methodIDCount, catDict, invokeType)

                        if (inMethod) and ('invoke-direct' in line):
                            invokeType = 'invoke-direct'
                            dataStructureHelper(catagory, appName, line, methodIDCount, catDict, invokeType)

                        if (inMethod) and ('invoke-super' in line):
                            invokeType = 'invoke-super'
                            dataStructureHelper(catagory, appName, line, methodIDCount, catDict, invokeType)

                        if (inMethod) and ('invoke-interface' in line):
                            invokeType = 'invoke-interface'
                            dataStructureHelper(catagory, appName, line, methodIDCount, catDict, invokeType)

            getUniqueAPIs(catDict, catagory, appName)

    malware = malware_app_paths()[:numMal]
    count = 0
    print("Loading Malware Apps into Data Structure....")
    for location in tqdm(malware):
        name = 'Malware_' + str(count)
        count = count + 1
        smaliFile = location + '/' + 'smali'
        if os.path.isdir(smaliFile):
            #go into smali file and get all the .methods and .endmethods using regex
            #assign unique id for each method (key) which will have a list of API calls for the values
            samliFiles = glob.glob(smaliFile + '/**/*.smali', recursive=True)
            #read each smali file and get the method calls
            for file in samliFiles:
                f = open(file, "r")
                Lines = f.readlines()
                for line in Lines:
                    if startMethod in line:
                        inMethod = True

                    if inMethod and (endMethod in line):
                        inMethod = False
                        methodIDCount += 1
                        methodList = []

                    if (inMethod) and ('invoke-static' in line):
                        invokeType = 'invoke-static'
                        dataStructureHelper('Malware', name, line, methodIDCount, catDict, invokeType)

                    if (inMethod) and ('invoke-virtual' in line):
                        invokeType = 'invoke-virtual'
                        dataStructureHelper('Malware', name, line, methodIDCount, catDict, invokeType)

                    if (inMethod) and ('invoke-direct' in line):
                        invokeType = 'invoke-direct'
                        dataStructureHelper('Malware', name, line, methodIDCount, catDict, invokeType)

                    if (inMethod) and ('invoke-super' in line):
                        invokeType = 'invoke-super'
                        dataStructureHelper('Malware', name, line, methodIDCount, catDict, invokeType)

                    if (inMethod) and ('invoke-interface' in line):
                        invokeType = 'invoke-interface'
                        dataStructureHelper('Malware', name, line, methodIDCount, catDict, invokeType)

            getUniqueAPIs(catDict, 'Malware', name)

    #Store the created Data Structure/dictionary as a json
    with open('completeDictionarySmall.json', 'w') as f:
        json.dump(catDict, f)
    
    return catDict
