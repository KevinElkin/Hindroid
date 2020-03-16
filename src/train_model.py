import numpy as np
from collections import defaultdict
import simplejson as json
import collections
import pandas as pd
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
import random
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import io
import os
import itertools
import pathlib
import re
from scipy import sparse
from sklearn import svm
from sklearn.svm import LinearSVC
from scipy.stats import uniform
from tqdm import tqdm


#---------------------------------------------Kernel multiplication----------------------------------------------------------#

# Transpose
def trans(Matrix):
    return Matrix.transpose()

# AA^T
def AAtrans(MatrixA, MatrixATrans):
    return MatrixA.dot(MatrixATrans)

# ABA^T
def ABAtrans(MatrixA, MatrixB, MatrixATrans):
    AdotB = MatrixA.dot(MatrixB)
    return AdotB.dot(MatrixATrans)

# APA^T
def APAtrans(MatrixA, MatrixP, MatrixATrans):
    AdotP = MatrixA.dot(MatrixP)
    return AdotP.dot(MatrixATrans)

# APBP^TA^T
def APBPtransAtrans(MatrixA, MatrixB, MatrixP, MatrixATrans, MatrixPTrans):
    AdotP = MatrixA.dot(MatrixP)
    AdotPdotB = AdotP.dot(MatrixB)
    prevDotPtrans = AdotPdotB.dot(MatrixPTrans)
    prevDotAtrans = prevDotPtrans.dot(MatrixATrans)
    return prevDotAtrans

def createSVM(ker, UniqueIDApp, MatrixKer):

    df = pd.DataFrame(ker)
    df['Classification_id'] = UniqueIDApp.keys()
    df['Classification_id'] = df['Classification_id'].apply(lambda x: 'malware' if 'Malware' in x else 'benign')

    feature_cols = df.iloc[:,:-1]
    X = feature_cols # Features
    y = df['Classification_id'] # Target variable

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.20, random_state = 42)
    clf = LinearSVC(random_state=0, tol=1e-5)
    fitted = clf.fit(X_train, y_train)
    pred = fitted.predict(X_test)
    accuracy = fitted.score(X_test, y_test)
    print('----------------------------------------------------------')
    print('Accuracy:  ' + str(accuracy))
    print('----------------------------------------------------------')
    f1 = f1_score(y_test, pred, average='weighted', labels=np.unique(pred))
    print('F1_score:  ' + str(f1))
    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
    print('Confusion_matrix')
    print('----------------------------------------------------------')
    print('tn: ' + str(tn) + '  |  fp: ' + str(fp) + '  |  fn: ' + str(fn) + '  |  tp: ' + str(tp))

    name = MatrixKer
    per = tp / (tp + fp)
    rec = tp / (tp + fn)
    file = open(str(MatrixKer),"w")

    file.write('Accuracy:  ' + str(accuracy) + '\n')
    file.write('F1_score:  ' + str(f1) + '\n')
    file.write('Confusion_matrix  ---->  ' + 'tn: ' + str(tn) + '  |  fp: ' + str(fp) + '  |  fn: ' + str(fn) + '  |  tp: ' + str(tp) + '\n')
    file.write('Percision:  ' + str(per) + '\n')
    file.write('Recall:  ' + str(rec) + '\n')
    file.close()
