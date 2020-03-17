
# Project Overview

This project aims to classify malware in android apps by studying the relationship between different API calls. Ulike primative malware detetion systems, the hindroid approach will examine 4 unique relationships between api calls; it analyzes the relationship between API calls and applications (A-Matrix), the relationship between API calls in the same code block (B-Matrix), the relationship between API calls and their package type (P-Matrix), and the relationship between API calls and their invoke type (I-Matrix). These features are then combined into a single kernel which will represent the features for the model to train on. The model in this implementation will focus on the following 4 kernels: AA^T, ABA^T, APA^T, and APBP^TA^T. This report will then train a LinearSVC model on each of the kernels and then test them with a subset of data (80% training - 20% testing). The model will then be assesed on their preformance based on the following metrics: F1 Score, Accuracy Score, Percesion, Recall, and a Confusion matrix. 

## Usage Instructions

* Using the command `python3 run.py test-project` will test the pipeline on a small subset of data. Currently, this will pull benign applications from the weather catagory and get an equal amount of malware applications to test with. 

## Description of Contents

The project consists of these portions:
```
PROJECT
├── .gitignore
├── README.md
├── config
│   ├── data-params-apk.json
│   ├── test-params.json
│   └── env.json
├── data
│   ├── apks
│   └── smalis
├── notebooks
│   └── .gitkeep
├── references
│   └── Hindroid.pdf
├── requirements.txt
├── run.py
└── src
    ├── etl.py
    ├── make_dataset.py
    ├── build_features.py
    └── train_model.py
    
```

### `src`

* `etl.py`: Library code that executes tasks useful for getting data. 

* `make_dataset.py`: Library code that creates the main data structure used during feature extraction

* `build_features.py`: Library code that will create the A-Matrix, B-Matrix, P-Matrix, and I-Matrix

* `train_model.py`: Library code that trains the model with the given features produced from build_features.py on a LinearSVC model

### `config`

* `data-params-apk.json`: Common parameters for getting data, serving as
  inputs to library code.
  
* `test-params.json`: Parameters for running small process on small
  test data.
  
* `env.json`: Contains the necessary docker image and outpaths from the model results
  
### `references`

* `Hindroid.pdf`: The main report refernenced during the creation of this project

### `notebooks`

* Jupyter notebooks for *analyses*
  - notebooks are not for data processing; they should import code
    from `src`.
    
    

### File Descriptions

`CATEGORY_Links_APK.txt:` A file containing a contcatinated version of all the xml
files for that catagory. This file will be found in the cooresponding catagory directory.
k number of sample xml files will be randomly sampled from this text files

`CATAGORY_Download_Page_Links_APK.txt:` A file that contains links to the pages to
click on the "download" button to get the apk files.

`CATAGORY_Download_Links_APK.txt:` A file containing the links that will automatically
download the apk files when typed into a browser. These urls will download the apk
files when requested.

`CATAGORY_K:` Represents the apk file that has been downloaded and converted to
smali code.

`completeDictionarySmall.json:` The data structure that has been created in make_dataset.py converted to a JSON.

`AA^T.txt:` A file containing the f1 score, accuracy score, percesion, recall, and a confusion matrix after the model has been tested on a test set of data for the AA^T kernel. 

`ABA^T.txt:` A file containing the f1 score, accuracy score, percesion, recall, and a confusion matrix after the model has been tested on a test set of data for the ABA^T kernel. 

`APA^T.txt:` A file containing the f1 score, accuracy score, percesion, recall, and a confusion matrix after the model has been tested on a test set of data for the APA^T kernel. 

`APBP^TA^T.txt:` A file containing the f1 score, accuracy score, percesion, recall, and a confusion matrix after the model has been tested on a test set of data for the APBP^TA^T kernel. 


