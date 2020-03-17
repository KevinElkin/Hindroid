from src.etl import *
from src.build_features import *
from src.train_model import *
from src.make_dataset import *
import sys
import warnings

def get_data(**kwargs):

    catagories = kwargs['catagories']
    sampleSize = kwargs['sampleSize']
    sitemap = kwargs['sitemap']
    path = createDir()

    gzlist = getSitemap(sitemap)
    catDicGz = gzLinkSort(gzlist)
    getGzCats(catDicGz, catagories, path)
    downloadAPK(catagories, sampleSize, path)
    getAPK(catagories, path)
    removeNoSmali(path)


if __name__== "__main__":
    warnings.filterwarnings("ignore")
    if sys.argv[1] == 'test-project':
        cfg = json.load(open('config/test-params.json'))
        get_data(**cfg)
    else:
        cfg = json.load(open('config/data-params-apk.json'))
        get_data(**cfg)


def main():

    PATH = findDir()
    DATA = 'completeDictionarySmall.json'

    print("Creating Data Structure")
    print('------------------------------------------------------------------------------------')

    catDict = createDataStructure(PATH)
    print('------------------------------------------------------------------------------------')
    print("Data Structure created")
    print('------------------------------------------------------------------------------------')

    print("Loading in the JSON file (Data Structure)....")
    print('------------------------------------------------------------------------------------')
    #f = open(DATA)
    #catDict = json.load(f)

    print("JSON File Loaded")
    print('------------------------------------------------------------------------------------')

    UniqueIDAPI = uniqueDict(catDict)
    UniqueIDApp = UniqueApps(catDict)

    print("Creating the Matricies")
    print('------------------------------------------------------------------------------------')
    aMatrix = aMatrixSparse(catDict, UniqueIDAPI, UniqueIDApp)
    pMatrix = pMatrixSparse(catDict, UniqueIDAPI)
    bMatrix = bMatrixSparse(catDict, UniqueIDAPI)
    print('------------------------------------------------------------------------------------')
    print("Matricies Created")
    print('------------------------------------------------------------------------------------')

    print('\n')
    print('Creating Model with Kernel: AA^T')
    createSVM(AAtrans(aMatrix, aMatrix.T).toarray(), UniqueIDApp, 'AA^T')
    print('------------------------------------------------------------------------------------')
    print('\n')
    print('Creating Model with Kernel: ABA^T')
    createSVM(ABAtrans(aMatrix, bMatrix, aMatrix.T).toarray(), UniqueIDApp, 'ABA^T')
    print('------------------------------------------------------------------------------------')
    print('\n')
    print('Creating Model with Kernel: APA^T')
    createSVM(APAtrans(aMatrix, pMatrix, aMatrix.T).toarray(), UniqueIDApp, 'APA^T')
    print('------------------------------------------------------------------------------------')
    print('\n')
    print('Creating Model with Kernel: APBP^TA^T')
    createSVM(APBPtransAtrans(aMatrix, bMatrix, pMatrix, aMatrix.T, pMatrix.T).toarray(), UniqueIDApp, 'APBP^TA^T')
    print('------------------------------------------------------------------------------------')


if __name__ == main():
    main()

