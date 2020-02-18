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
import io
import gzip
import random
import os
import pathlib
import re

'''
***Note: I a currently still creating the run.py file in the form it was supposed to
be in for Assignment 2. Despite this, all other tasks have been properly completed in full.
I have successfully completed the EDA and created and tested a variety of different models
on my findings from my EDA. Additionally, all 4 of the Matrices (MatrixA, MatrixB, MatrixP, and MatrixI)
have been implemented successfully and work as intended. I look forward to attending office hours to ask
questions and get feedback on what I have done thus far.

Also, I do realize that much of this code is redundant and definitely needs to be modularized - I am working on that
continuously. I have changed up my implementation(s) and approaches multiple times and it definitely shows through the
current state of my code. 
'''

PATH = '/Users/kelkin/Documents/DSC_180A/APK_Downloads/'

list_subfolders_with_paths = [f.path for f in os.scandir(PATH) if f.is_dir()]



directDic = {}

for direct in list_subfolders_with_paths[:-1]:
    subdirs = []
    for sub in os.scandir(direct):
        if sub.is_dir():
            subdirs.append(sub.name)
    directDic[direct.split("/")[-1]] = subdirs


catDict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))


methodIDCount = 0
methodID = 'method_' + str(methodIDCount)
methodList = []
inMethod = False
startMethod = '.method'
endMethod = '.end method'
patAPI = re.compile('^[^}]*}')
patPack = re.compile('^(.*?)->')





for catagory in directDic:

    for appName in directDic[catagory]:
        #get path of appname in dir
        newPath = PATH + str(catagory) + '/' + str(appName) + '/' + 'smali'
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
                        methodID = 'method_' + str(methodIDCount)
                        result = re.sub(patAPI, '', line)

                        apiCall = result[2:-2]
                        package = re.search(patPack, apiCall)

                        catDict[catagory][appName]['Packages'][package.group(1)].append(apiCall)
                        catDict[catagory][appName]['All_APIs']['APIs'].append(apiCall)
                        catDict[catagory][appName]['Invoke_Type']['invoke-static'].append(apiCall)
                        catDict[catagory][appName]['Methods'][methodID].append(apiCall)

                    if (inMethod) and ('invoke-virtual' in line):
                        methodID = 'method_' + str(methodIDCount)
                        result = re.sub(patAPI, '', line)
                        apiCall = result[2:-2]
                        package = re.search(patPack, apiCall)

                        catDict[catagory][appName]['Packages'][package.group(1)].append(apiCall)
                        catDict[catagory][appName]['All_APIs']['APIs'].append(apiCall)
                        catDict[catagory][appName]['Invoke_Type']['invoke-virtual'].append(apiCall)
                        catDict[catagory][appName]['Methods'][methodID].append(apiCall)

                    if (inMethod) and ('invoke-direct' in line):
                        methodID = 'method_' + str(methodIDCount)
                        result = re.sub(patAPI, '', line)
                        apiCall = result[2:-2]
                        package = re.search(patPack, apiCall)

                        catDict[catagory][appName]['Packages'][package.group(1)].append(apiCall)
                        catDict[catagory][appName]['All_APIs']['APIs'].append(apiCall)
                        catDict[catagory][appName]['Invoke_Type']['invoke-direct'].append(apiCall)
                        catDict[catagory][appName]['Methods'][methodID].append(apiCall)

                    if (inMethod) and ('invoke-super' in line):
                        methodID = 'method_' + str(methodIDCount)
                        result = re.sub(patAPI, '', line)
                        apiCall = result[2:-2]
                        package = re.search(patPack, apiCall)

                        catDict[catagory][appName]['Packages'][package.group(1)].append(apiCall)
                        catDict[catagory][appName]['All_APIs']['APIs'].append(apiCall)
                        catDict[catagory][appName]['Invoke_Type']['invoke-super'].append(apiCall)
                        catDict[catagory][appName]['Methods'][methodID].append(apiCall)

                    if (inMethod) and ('invoke-interface' in line):
                        methodID = 'method_' + str(methodIDCount)
                        result = re.sub(patAPI, '', line)
                        apiCall = result[2:-2]
                        package = re.search(patPack, apiCall)

                        catDict[catagory][appName]['Packages'][package.group(1)].append(apiCall)
                        catDict[catagory][appName]['All_APIs']['APIs'].append(apiCall)
                        catDict[catagory][appName]['Invoke_Type']['invoke-interface'].append(apiCall)
                        catDict[catagory][appName]['Methods'][methodID].append(apiCall)

        catDict[catagory][appName]['Invoke_Type']['invoke-static'] = set(catDict[catagory][appName]['Invoke_Type']['invoke-static'])
        catDict[catagory][appName]['Invoke_Type']['invoke-virtual'] = set(catDict[catagory][appName]['Invoke_Type']['invoke-virtual'])
        catDict[catagory][appName]['Invoke_Type']['invoke-direct'] = set(catDict[catagory][appName]['Invoke_Type']['invoke-direct'])
        catDict[catagory][appName]['Invoke_Type']['invoke-super'] = set(catDict[catagory][appName]['Invoke_Type']['invoke-super'])
        catDict[catagory][appName]['Invoke_Type']['invoke-interface'] = set(catDict[catagory][appName]['Invoke_Type']['invoke-interface'])
        catDict[catagory][appName]['All_APIs']['APIs'] = set(catDict[catagory][appName]['All_APIs']['APIs'])

        for pack in catDict[catagory][appName]['Packages']:
            catDict[catagory][appName]['Packages'][pack] = set(catDict[catagory][appName]['Packages'][pack])



#get a list of every possible api call in all the apps and take the set of it. This will be the
allAPIs = []
for catagory in catDict:
    for appName in catDict[catagory]:
        allAPIs = allAPIs + list(catDict[catagory][appName]['All_APIs']['APIs'])
allAPIs = list(set(allAPIs))


# Make a new dictionary containing unique API and there index
UniqueIDAPI = {}
idMaker = 0
for i in allAPIs:
    UniqueIDAPI[i] = idMaker
    idMaker += 1




#get all the possible app names
allApps = []
for catagory in catDict:
    allApps = allApps + list(catDict[catagory])


# Make a new dictionary containing unique apps and there index
UniqueIDApp = {}
idMakerApp = 0
for i in allApps:
    UniqueIDApp[i] = idMakerApp
    idMakerApp += 1

######MATRICIES######
#---------------------------------------------------------------------------------------------------------#
# Create a matrix containing app names as the rows and column names as the set of apis between all apps

rows, cols = len(allApps), len(allAPIs)
MatrixA = np.zeros(shape=(rows,cols),dtype=int)

for catagory in catDict:
    for appName in catDict[catagory]:
        appIdx = UniqueIDApp[appName]
        for api in list(catDict[catagory][appName]['All_APIs']['APIs']):
            apiIdx = UniqueIDAPI[api]
            MatrixA[appIdx][apiIdx] = 1


#-----------------------------------------------------------------------------------------------------------#
#Find the adjacency matrix for methods that exist in the same code block MatrixB

methods = list(catDict[catagory][appName]['Methods'])
rows, cols = len(allAPIs), len(allAPIs)
MatrixB = np.zeros(shape = (rows, cols),dtype=int)

for catagory in catDict:
    for appName in catDict[catagory]:
        keylist = list(catDict[catagory][appName]['Methods'].keys())
        methodList = [[item for item in catDict[catagory][appName]['Methods'][key]] for key in keylist]

        for i in methodList:
            for j in i:
                for k in i:
                    MatrixB[UniqueIDAPI[k]][UniqueIDAPI[j]] = 1
                    MatrixB[UniqueIDAPI[j]][UniqueIDAPI[k]] = 1
#-----------------------------------------------------------------------------------------------------------#
#Find the adjacency matrix for methods that exist in the same package MatrixP

packages = list(catDict[catagory][appName]['Packages'])
rows, cols = len(allAPIs), len(allAPIs)
MatrixP = np.zeros(shape = (rows, cols),dtype=int)

for catagory in catDict:
    for appName in catDict[catagory]:
        keylist = list(catDict[catagory][appName]['Packages'].keys())
        packageList = [[item for item in catDict[catagory][appName]['Packages'][key]] for key in keylist]

        for i in packageList:
            for j in i:
                for k in i:
                    MatrixP[UniqueIDAPI[k]][UniqueIDAPI[j]] = 1
                    MatrixP[UniqueIDAPI[j]][UniqueIDAPI[k]] = 1
#-----------------------------------------------------------------------------------------------------------#
#Find the adjacency matrix for methods that exist in the same invoke method MatrixI

invokes = list(catDict[catagory][appName]['Invoke_Type'])
rows, cols = len(allAPIs), len(allAPIs)
MatrixI = np.zeros(shape = (rows, cols), dtype=int)

for catagory in catDict:
    for appName in catDict[catagory]:
        keylist = list(catDict[catagory][appName]['Invoke_Type'].keys())
        invokeList = [[item for item in catDict[catagory][appName]['Invoke_Type'][key]] for key in keylist]

        for i in invokeList:
            for j in i:
                for k in i:
                    MatrixI[UniqueIDAPI[k]][UniqueIDAPI[j]] = 1
                    MatrixI[UniqueIDAPI[j]][UniqueIDAPI[k]] = 1
#-----------------------------------------------------------------------------------------------------------#





##### Begin EDA #####

### Get the number of unique API calls
totalBeauty = 4
totalComics = 10

ApiListBeauty = []
ApiListComics = []
PackListBeauty = 0
PackListComics = 0

staticBeauty = 0
virtualBeauty = 0
directBeauty = 0
superBeauty = 0
interfaceBeauty = 0

staticComics = 0
virtualComics = 0
directComics = 0
superComics = 0
interfaceComics = 0

for appName in catDict['beauty']:
    ApiListBeauty = ApiListBeauty + list(catDict['beauty'][appName]['All_APIs']['APIs'])
ApiListBeauty = set(ApiListBeauty)

for appName in catDict['comics']:
    ApiListComics = ApiListComics + list(catDict['comics'][appName]['All_APIs']['APIs'])
ApiListComics = set(ApiListComics)

totalNumUniqueBeauty = len(ApiListBeauty)
totalNumUniqueComics = len(ApiListComics)

print('totalNumUniqueBeauty: ' + str(totalNumUniqueBeauty) +'\n')
print('totalNumUniqueComics: ' + str(totalNumUniqueComics) +'\n')

avgUniqueBeauty = totalNumUniqueBeauty / totalComics
avgUniqueComics = totalNumUniqueComics / totalBeauty

print('avgUniqueBeauty: ' + str(avgUniqueBeauty) +'\n')
print('avgUniqueComics: ' + str(avgUniqueComics) +'\n')
print('----------------------------------------------------\n')

### Get the total number of Packages

for appName in catDict['beauty']:
    for pack in catDict['beauty'][appName]['Packages']:
        PackListBeauty = PackListBeauty + len(list(catDict['beauty'][appName]['Packages'][pack]))


for appName in catDict['comics']:
     for pack in catDict['comics'][appName]['Packages']:
        PackListComics = PackListComics + len(list(catDict['comics'][appName]['Packages'][pack]))


totalNumPackBeauty = PackListBeauty
totalNumPackComics = PackListComics

print('totalNumPackBeauty: ' + str(totalNumPackBeauty) +'\n')
print('totalNumPackComics: ' + str(totalNumPackComics) +'\n')

avgUniquePackBeauty = totalNumPackBeauty / totalBeauty
avgUniquePackComics = totalNumPackComics / totalComics

print('avgUniquePackBeauty: ' + str(avgUniquePackBeauty) +'\n')
print('avgUniquePackComics: ' + str(avgUniquePackComics) +'\n')
print('----------------------------------------------------\n')
### Number of API calls by type per catagory

for appName in catDict['beauty']:

    staticBeauty = staticBeauty + len(list(catDict['beauty'][appName]['Invoke_Type']['invoke-static']))
    virtualBeauty = virtualBeauty + len(list(catDict['beauty'][appName]['Invoke_Type']['invoke-virtual']))
    directBeauty = directBeauty + len(list(catDict['beauty'][appName]['Invoke_Type']['invoke-direct']))
    superBeauty = superBeauty + len(list(catDict['beauty'][appName]['Invoke_Type']['invoke-super']))
    interfaceBeauty = interfaceBeauty + len(list(catDict['beauty'][appName]['Invoke_Type']['invoke-interface']))

for appName in catDict['comics']:

    staticComics = staticComics + len(list(catDict['comics'][appName]['Invoke_Type']['invoke-static']))
    virtualComics = virtualComics + len(list(catDict['comics'][appName]['Invoke_Type']['invoke-virtual']))
    directComics = directComics + len(list(catDict['comics'][appName]['Invoke_Type']['invoke-direct']))
    superComics = superComics + len(list(catDict['comics'][appName]['Invoke_Type']['invoke-super']))
    interfaceComics = interfaceComics + len(list(catDict['comics'][appName]['Invoke_Type']['invoke-interface']))

### Average number of API calls by invoke type

staticBeautyAvg = staticBeauty / totalBeauty
virtualBeautyAvg = virtualBeauty / totalBeauty
directBeautyAvg = directBeauty / totalBeauty
superBeautyAvg = superBeauty / totalBeauty
interfaceBeautyAvg = interfaceBeauty / totalBeauty

staticComicsAvg = staticComics / totalComics
virtualComicsAvg = virtualComics / totalComics
directComicsAvg = directComics / totalComics
superComicsAvg = superComics / totalComics
interfaceComicsAvg = interfaceComics / totalComics


print('staticBeautyAvg: ' + str(staticBeautyAvg) +'\n')
print('virtualBeautyAvg: ' + str(virtualBeautyAvg) +'\n')
print('directBeautyAvg: ' + str(directBeautyAvg) +'\n')
print('superBeautyAvg: ' + str(superBeautyAvg) +'\n')
print('interfaceBeautyAvg: ' + str(interfaceBeautyAvg) +'\n')
print('----------------------------------------------------\n')

print('staticComicsAvg: ' + str(staticComicsAvg) +'\n')
print('virtualComicsAvg: ' + str(virtualComicsAvg) +'\n')
print('directComicsAvg: ' + str(directComicsAvg) +'\n')
print('superComicsAvg: ' + str(superComicsAvg) +'\n')
print('interfaceComicsAvg: ' + str(interfaceComicsAvg) +'\n')
print('----------------------------------------------------\n')

### Number of unique API calls by invoke type

# staticBeautyUniq = set(staticBeauty)
# virtualBeautyUniq = set(staticBeauty)
# directBeautyUniq = set(staticBeauty)
# superBeautyUniq = set(staticBeauty)
# interfaceBeautyUniq = set(staticBeauty)

# staticComicsUniq = set(staticBeauty)
# virtualComicsUniq = set(staticBeauty)
# directComicsUniq = set(staticBeauty)
# superComicsUniq = set(staticBeauty)
# interfaceComicsUniq = set(staticBeauty)

# print('staticBeautyUniq: ' + str(staticBeautyUniq) +'\n')
# print('virtualBeautyUniq: ' + str(virtualBeautyUniq) +'\n')
# print('directBeautyUniq: ' + str(directBeautyUniq) +'\n')
# print('superBeautyUniq: ' + str(superBeautyUniq) +'\n')
# print('interfaceBeautyUniq: ' + str(interfaceBeautyUniq) +'\n')
# print('----------------------------------------------------\n')

# print('staticComicsUniq: ' + str(staticComicsUniq) +'\n')
# print('virtualComicsUniq: ' + str(virtualComicsUniq) +'\n')
# print('directComicsUniq: ' + str(directComicsUniq) +'\n')
# print('superComicsUniq: ' + str(superComicsUniq) +'\n')
# print('interfaceComicsUniq: ' + str(interfaceComicsUniq) +'\n')
# print('----------------------------------------------------\n')



# Create a Baseline Model to classify type of app catagory based on there invoke type counts and there number of unique packages
catagory = [0,0,0,0,1,1,1,1,1,1,1,1,1]
staticBeautyLi = []
virtualBeautyLi = []
directBeautyLi = []
superBeautyLi = []
interfaceBeautyLi = []

staticComicsLi = []
virtualComicsLi = []
directComicsLi = []
superComicsLi = []
interfaceComicsLi = []

uniqueComicPack = []
uniqueBeautyPack = []

comicsAppName = []
beautyAppName = []

for appName in catDict['comics']:
    superComicsLi.append(len(list(catDict['comics'][appName]['Invoke_Type']['invoke-super'])))
    interfaceComicsLi.append(len(list(catDict['comics'][appName]['Invoke_Type']['invoke-interface'])))
    directComicsLi.append(len(list(catDict['comics'][appName]['Invoke_Type']['invoke-direct'])))
    virtualComicsLi.append(len(list(catDict['comics'][appName]['Invoke_Type']['invoke-virtual'])))
    staticComicsLi.append(len(list(catDict['comics'][appName]['Invoke_Type']['invoke-static'])))
    comicsAppName.append(appName)

for appName in catDict['beauty']:
    superBeautyLi.append(len(list(catDict['beauty'][appName]['Invoke_Type']['invoke-super'])))
    interfaceBeautyLi.append(len(list(catDict['beauty'][appName]['Invoke_Type']['invoke-interface'])))
    directBeautyLi.append(len(list(catDict['beauty'][appName]['Invoke_Type']['invoke-direct'])))
    virtualBeautyLi.append(len(list(catDict['beauty'][appName]['Invoke_Type']['invoke-virtual'])))
    staticBeautyLi.append(len(list(catDict['beauty'][appName]['Invoke_Type']['invoke-static'])))
    beautyAppName.append(appName)

interfaceBeautyLi = interfaceBeautyLi[:4]
directBeautyLi = directBeautyLi[:4]
virtualBeautyLi = virtualBeautyLi[:4]
staticBeautyLi = staticBeautyLi[:4]
superBeautyLi = superBeautyLi[:4]
beautyAppName = beautyAppName[:4]


comicsAppName = comicsAppName[1:10]
superComicsLi = superComicsLi[1:10]
interfaceComicsLi = interfaceComicsLi[1:10]
directComicsLi = directComicsLi[1:10]
virtualComicsLi = virtualComicsLi[1:10]
staticComicsLi = staticComicsLi[1:10]

beautyAppName = beautyAppName + comicsAppName
interfaceBeautyLi = interfaceBeautyLi + interfaceComicsLi
directBeautyLi = directBeautyLi + directComicsLi
virtualBeautyLi = virtualBeautyLi + virtualComicsLi
superBeautyLi = superBeautyLi + superComicsLi
staticBeautyLi = staticBeautyLi + staticComicsLi



df = pd.DataFrame()
df['AppName'] = beautyAppName
df['Interface Invoke'] = interfaceBeautyLi
df['Direct Invoke'] = directBeautyLi
df['Virtual Invoke'] = virtualBeautyLi
df['Super Invoke'] = superBeautyLi
df['Static Invoke'] = staticBeautyLi
df['label'] = catagory


feature_cols = ['Interface Invoke', 'Direct Invoke', 'Virtual Invoke', 'Super Invoke','Static Invoke']
X = df[feature_cols] # Features
y = df.label # Target variable

logreg = RandomForestClassifier()
fitted = logreg.fit(X,y)
pred = fitted.predict(X)
fitted.score(X,y)
f1 = f1_score(y, pred, average='weighted')
f1
