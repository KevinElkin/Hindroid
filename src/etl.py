import requests
from bs4 import BeautifulSoup
import urllib.request
from collections import defaultdict
import simplejson as json
import random
import io
import gzip
import random
import os
import re
import shutil
from tqdm import tqdm


'''
----------------------------------------------------------------------------------
FILE DESRIPTIONS:

CATEGORY_Links_APK.txt - A file containing a contcatinated version of all the xml
files for that catagory. This file will be found in the cooresponding catagory directory.
k number of sample xml files will be randomly sampled from this text files

CATAGORY_Download_Page_Links_APK.txt - A file that contains links to the pages to
click on the "download" button to get the apk files.

CATAGORY_Download_Links_APK.txt - A file containing the links that will automatically
download the apk files when typed into a browser. These urls will download the apk
files when requested.

CATAGORY_K - Represents the apk file that has been downloaded and converted to
smali code

'''

'''
Go back one directory and then return the current working directory
'''
def findDir():
    os.chdir('..')
    return os.getcwd()
s
'''
A method that creates the necessary file structure that will be used to
store the APK downloads
'''

def createDir():

    cwd = os.getcwd()
    file = str(cwd) + '/Test_Project'
    file2 = file + '/APK_Downloads/'
    
    if os.path.isdir(file) == False:
        os.mkdir(file)
        if os.path.isdir(file2) == False:
            os.mkdir(file2)

    return file2


'''
A method that obtains all the gz files from the given url

url - the sitemap url for apkpure
'''
def getSitemap(url):

    url = requests.get(url).text
    soup = BeautifulSoup(url, 'lxml')

    li = []

    for elem in soup.find_all('loc'):
        li.append(elem.text)

    return li


'''
A method that returns a dictionary of gz urls based on there catagory.
the key represents the catagory and the values are a list of urls that
fall under the given catagory


gzlist - the list of gz files obtained from calling getSitemap
'''
def gzLinkSort(gzlist):

    firstPart = 'https://apkpure.com/sitemaps/'
    sep = '-'
    sep2 = '.'

    gzCat = defaultdict(list)
    links = []

    for url in gzlist:

        cat = url.split(firstPart, 1)[1]
        if '-' in cat:
            cat = cat.split(sep, 1)[0]
        else:
            cat = cat.split(sep2, 1)[0]
        gzCat[cat].append(url)

    return gzCat



'''
A method that goes through the xml files of the catagories found in the getGzCats
method and stores all the links in a text file. These links are links that contain
the page where we can download the apk files. This method is intended to be a
helper method for getGzCats.

outFile - the xml file of the catagory to be taken in. This will then be searched through
to find the links coresponding to the download pages of the apk

path - the location you want your xml files to be downloaded to

'''
def findLocs(outFile, path):

    file = open(outFile, 'r')
    line = file.readlines()

    locs = []
    for url in line:
        soup = BeautifulSoup(url, 'lxml')
        data = soup.find_all('loc')

        for i in data:
            locs.append(i.text)
    return locs


'''
A method that takes in a dictionary (catagory (key), list of gz url (values))
and the given catagories you wish to obtain the xml files of. The path specifies where
the xml files will be downloaded. Do note that the xml files will be inserted into
a directory with the corresponding name of the catagory

gzDict - a dictionary containing the catagories of gz files and their assosiated links

catagories - the catagories of gz files you want to obtain the xml files for

path - the location you want your xml files to be downloaded to

'''
def getGzCats(gzDict, catagories, path):

    firstPart = 'https://apkpure.com/sitemaps/'
    os.chdir(path)

    for cat in catagories:

        os.chdir(path)

        if not os.path.exists(cat):
            os.makedirs(cat)

        newPath = path + str(cat)
        os.chdir(newPath)
        
        print("\nCollecting gz files for the " + str(cat) + " catagory....\n")
        
        for file in gzDict[cat]:
            print(file)
            response = requests.get(file)
            compressed_file = io.BytesIO(response.content)
            decompressed_file = gzip.GzipFile(fileobj = compressed_file)
            out = str(cat) + '.xml'

            with open(out, 'wb') as outfile:
                outfile.write(decompressed_file.read())


            out2 = str(cat) + '_Links_APK' + '.txt'

            apklinks = findLocs(out, path)

            with open(out2, 'w') as outfile:
                outfile.write("\n".join(apklinks))


'''
A method that randomly samples k number of apk urls from
a specified filename (ex. comics_Links_APK.txt)

filename - the specified txt file to sample from

k - the numebr of samples you wish to obtain for a given
catagory

'''
def random_sampler(filename, k):

    sample = []
    with open(filename, 'rb') as f:
        linecount = sum(1 for line in f)
        f.seek(0)

        random_linenos = sorted(random.sample(range(linecount), k), reverse = True)
        lineno = random_linenos.pop()
        for n, line in enumerate(f):
            if n == lineno:
                sample.append(line.rstrip())
                if len(random_linenos) > 0:
                    lineno = random_linenos.pop()
                else:
                    break
    return sample


'''
Get the link to the downloads page for apk on the main page.
These links will direct us to the download page.

num - specifies the number of links you wish to obtain

catagories - A list of the catagories of apps you wish to call from

path - the location you want your xml files to be downloaded to

'''
def getDownloadLinks(catagories, num, path):


    for cat in catagories:

        filename = str(cat) + '_Links_APK.txt'
        newPath = path + str(cat) + '/' + filename

        
        randomFiles = random_sampler(newPath, num)
        #For demonstaration purposes grab first n links
        
#         with open(newPath) as myfile:
#             head = [next(myfile) for x in range(num)]

        dLinks = []
        dic = {}

        print("Collecting APK URLs for the " + str(cat) + " catagory....\n")
        for site in randomFiles:
            print(site)
            url = requests.get(site).text
            soup = BeautifulSoup(url, 'html.parser')
            try:
                apk = soup.find('div', attrs = {'class':'main page-q'}).find('div', attrs = {'class':'left'}).find('div', attrs = {'class':'box'}).find('dl', attrs = {'class':'ny-dl ny-dl-n'}).find('dd')
                apkWebsite = apk.find('div', attrs = {'class':'ny-down'}).find('a', attrs = {'class':'da'})
                name = apk.find('div', attrs = {'class':'title-like'}).find('h1')
                nameStr = str(name)[4:-5]
                downloadLink = apkWebsite.attrs['href']
                downloadLink = 'https://apkpure.com' + downloadLink
                dic[nameStr] = downloadLink
                dLinks.append(downloadLink)

                # Write sampled links to a text file
                out = path + str(cat) + '/' + str(cat) + '_Download_Page_Links_APK' + '.txt'

                with open(out, 'w') as outfile:
                    outfile.write("\n".join(dLinks))


            except AttributeError as err:
                #Cannot access file because of scrapping limitation stated 
                pass
                


    return dLinks


'''
A method designed to get the links to download the APK of a given
android app. These links will download the APK file when entered into
the browser

num - specifies the number of links you wish to obtain

catagories - A list of the catagories of apps you wish to call from

path - the location you want your xml files to be downloaded to

'''
def downloadAPK(catagories, num, path):

    listAPK = []

    getDownloadLinks(catagories, num, path)

    for cat in catagories:

        filename = str(cat) + '_Download_Page_Links_APK.txt'
        newPath = path + str(cat) + '/' + filename


        with open(newPath) as f:
            content = f.readlines()

        for site in content:

            names = []

            url = requests.get(site).text
            soup = BeautifulSoup(url, 'html.parser')

            try:
                apkDownload = soup.find('div', attrs = {'class':'main page-q'}).find('div', attrs = {'class':'left'}).find('div', attrs = {'class':'box'}).find('div', attrs = {'class':'fast-download-box fast-bottom'}).find('p', attrs = {'class':'down-click'}).find('a', attrs = {'id':'download_link'})
                listAPK.append(apkDownload.attrs['href'])
                names = apkDownload.attrs['title'][9:]

                # Write sampled links to a text file
                out = path + str(cat) + '/' + str(cat) + '_Download_Links_APK' + '.txt'

                with open(out, 'w') as outfile:
                    outfile.write("\n".join(listAPK))

            except AttributeError as err:
                #Cannot access file because of scrapping limitation stated 
                pass



'''
A method that gets the downloaded apk files from apkpure and
stores them in their correct catagory directory in APK_Downloads.
This method then converts the downloaded apk files into smali code
and stores it in the current catagory directory

catagories - A list of the catagories of apps you wish to call from

path - the location you want your xml files to be downloaded to
'''
def getAPK(catagories, path):

    for cat in catagories:

        filename = str(cat) + '_Download_Links_APK.txt'
        newPath = path + str(cat) + '/' + filename
        catDir = path + str(cat)

        with open(newPath) as f:
            content = f.readlines()

        count = 0
        for link in content:

            resp = requests.get(link, stream = True)
            contents = resp.content

            name = count

            out = os.path.join(catDir, str(cat) + '_' + str(name) +'.apk')

            with open( out, "wb" ) as code:
                code.write(contents)
                os.chdir(catDir)
                os.system('apktool d ' + str(cat) + '_' + str(name) +'.apk')

            count += 1

'''
A method that solves an issue encountered where a very few directories of apps do not contain
a smali subdirectory. This method will remove these files from the test data

path - the path to the directory of apps
'''
def removeNoSmali(path):

    list_subfolders_with_paths = [f.path for f in os.scandir(path) if f.is_dir()]

    for catPath in list_subfolders_with_paths:
        appNames = [f.path for f in os.scandir(catPath) if f.is_dir()]
        for app in appNames:
            subDirs = [f.path for f in os.scandir(app) if f.is_dir()]
            currPath = str(app) + '/' + 'smali'
            if (os.path.isdir(currPath)) == False:
                shutil.rmtree(app)
