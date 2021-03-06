import urllib.request
import numpy as np
from collections import defaultdict
import simplejson as json
import collections
import pandas as pd
import random
import io
import gzip
import os
import itertools
import pathlib
import re
from scipy import sparse
from scipy.stats import uniform
from tqdm import tqdm



#------------------------------------------------Matrix Indexing Dictionaries--------------------------------------------------


def allAPIsDataset(catDict):
    '''
    A method that will get every API call between all apps present in the dataset. This will be used
    for creating the AMatrix, BMatric, PMatrix and IMatrix implemented in the matrix section.

    :param catDict: a json file that has been written to disk containg the data structure created
    in the createDataStructure method call
    :returns: a list of all APIs
    '''
    
    #get a list of every possible api call in all the apps and take the set of it.
    print("Finding Indicies for each API....")
    allAPIs = []
    for catagory in tqdm(catDict):
        for appName in catDict[catagory]:
            allAPIs = allAPIs + list(catDict[catagory][appName]['All_APIs']['APIs'])
    allAPIs = list(set(allAPIs))

    return allAPIs



def uniqueDict(jsonFile):
    '''
    A Method that will create a dictionary using the set of all APIs returned in the allAPIsDataset
    method call. This method will allow for easy indexing rows/columns in the matricies created.

    :param jsonFile: a json file that has been written to disk containg the data structure created
    in the createDataStructure method call
    :returns: A dictionary of unique indicies for each API
    '''
    # Make a new dictionary containing unique API and there index
    UniqueIDAPI = {}
    idMaker = 0
    for i in allAPIsDataset(jsonFile):
        UniqueIDAPI[i] = idMaker
        idMaker += 1

    return UniqueIDAPI



def allApps(catDict):
    '''
    A method that will get every app name present in the dataset. This will be used
    for creating the AMatrix implemented in the matrix section.

    :param catDict: a json file that has been written to disk containg the data structure created
    in the createDataStructure method call
    :returns: A list of all possible app names in the dataset 
    '''
    
    #get all the possible app names
    allApps = []
    print("Finding Indicies for each App....")
    for catagory in tqdm(catDict):
        allApps = allApps + list(catDict[catagory])
    return allApps



def UniqueApps(jsonFile):
    '''
    A Method that will create a dictionary using all the app names returned in the allApps
    method call. This method will allow for easy indexing rows/columns in the matricies created.

    :param jsonFile: a json file that has been written to disk containg the data structure created
    in the createDataStructure method call
    :returns: A dictionary of unique indicies for each app
    '''
    UniqueIDApp = {}
    idMakerApp = 0

    # Make a new dictionary containing unique apps and there index
    for i in allApps(jsonFile):
        UniqueIDApp[i] = idMakerApp
        idMakerApp += 1

    return UniqueIDApp

#---------------------------------------------Matrix Creation----------------------------------------------------------#




def aMatrixSparse(catDict, UniqueIDAPI, UniqueIDApp):
    '''
    Creates the A Matrix using the Matrix Indexing Dictionaries - refer to written report for detailed
    description of the A MatrixA

    :param catDict: a json file that has been written to disk containg the data structure created
    in the createDataStructure method call
    :param UniqueIDAPI: A dictionary that contains APIs as keys and an index as a value
    :param UniqueIDApp: A dictionary that contains App Names as keys and an index as a value
    :returns: The A-Matrix
    '''
    appIdxRows = []
    apiIdxCols = []
    data = []
    print("Creating The A-Matrix....")
    for catagory in tqdm(catDict):
        for appName in catDict[catagory]:
            for api in list(catDict[catagory][appName]['All_APIs']['APIs']):
                appIdxRows.append(UniqueIDApp[appName])
                apiIdxCols.append(UniqueIDAPI[api])
                data.append(1)

    return sparse.coo_matrix((data, (appIdxRows, apiIdxCols)))



def bMatrixSparse(catDict, UniqueIDAPI):
    '''
    Creates the B Matrix using the Matrix Indexing Dictionaries - refer to written report for detailed
    description of the A MatrixB

    :param catDict: a json file that has been written to disk containg the data structure created
    in the createDataStructure method call
    :param UniqueIDAPI: A dictionary that contains APIs as keys and an index as a value
    :returns: The B-Matrix
    '''
    appIdxRows = []
    apiIdxCols = []
    data = []

    #Find the adjacency matrix for methods that exist in the same code block MatrixB
    print("Creating The B-Matrix....")
    for catagory in tqdm(catDict):
        for appName in catDict[catagory]:  
            keylist = list(catDict[catagory][appName]['Methods'].keys())

            methodList = [[item for item in catDict[catagory][appName]['Methods'][key]] for key in keylist]

            for i in methodList:
                for j in i:
                    for k in i:
                        appIdxRows.append(UniqueIDAPI[j])
                        apiIdxCols.append(UniqueIDAPI[k])
                        data.append(1)

                        appIdxRows.append(UniqueIDAPI[k])
                        apiIdxCols.append(UniqueIDAPI[j])
                        data.append(1)
    return sparse.coo_matrix((data, (appIdxRows, apiIdxCols)))


def pMatrixSparse(catDict, UniqueIDAPI):
    '''
    Creates the P Matrix using the Matrix Indexing Dictionaries - refer to written report for detailed
    description of the A MatrixP

    :param catDict: a json file that has been written to disk containg the data structure created
    in the createDataStructure method call
    :param UniqueIDAPI: A dictionary that contains APIs as keys and an index as a value
    :returns: The P-Matrix
    '''
    
    f = open(jsonFile)
    catDict = json.load(f)

    appIdxRows = []
    apiIdxCols = []
    data = []

    #Find the adjacency matrix for methods that exist in the same package MatrixP
    print("Creating The P-Matrix....")
    for catagory in tqdm(catDict):
        for appName in catDict[catagory]:
            keylist = list(catDict[catagory][appName]['Packages'].keys())
            packageList = [[item for item in catDict[catagory][appName]['Packages'][key]] for key in keylist]

            for i in packageList:
                for j in i:
                    for k in i:
                        appIdxRows.append(UniqueIDAPI[j])
                        apiIdxCols.append(UniqueIDAPI[k])
                        data.append(1)

                        appIdxRows.append(UniqueIDAPI[k])
                        apiIdxCols.append(UniqueIDAPI[j])
                        data.append(1)

    return sparse.coo_matrix((data, (appIdxRows, apiIdxCols)))



def iMatrixSparse(catDict, UniqueIDAPI):
    '''
    Creates the I Matrix using the Matrix Indexing Dictionaries - refer to written report for detailed
    description of the I MatrixA

    :param catDict: a json file that has been written to disk containg the data structure created
    in the createDataStructure method call
    :param UniqueIDAPI: A dictionary that contains APIs as keys and an index as a value
    :returns: The I-Matrix
    '''
    appIdxRows = []
    apiIdxCols = []
    data = []

    #Find the adjacency matrix for methods that exist in the same invoke method MatrixI
    print("Creating The I-Matrix....")
    for catagory in tqdm(catDict):
        for appName in catDict[catagory]:
            keylist = list(catDict[catagory][appName]['Invoke_Type'].keys())
            invokeList = [[item for item in catDict[catagory][appName]['Invoke_Type'][key]] for key in keylist]

            for i in invokeList:
                for j in i:
                    for k in i:
                        appIdxRows.append(UniqueIDAPI[j])
                        apiIdxCols.append(UniqueIDAPI[k])
                        data.append(1)

                        appIdxRows.append(UniqueIDAPI[k])
                        apiIdxCols.append(UniqueIDAPI[j])
                        data.append(1)

    return sparse.coo_matrix((data, (appIdxRows, apiIdxCols)))
