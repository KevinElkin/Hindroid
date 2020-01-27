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

'''
----------------------------------------------------------------------------------
LATEST VERSION:

This version contains a correct and proper implementation
using a configuration. My prior implementation worked but was unclean, confusing,
and unstructured. Upon revision I made sure to write clean and structured code that
can easily be changed and configured to fit different criteria such as catagory,
sample size, and the directory path. Additionally, I sucsessfully create a new directory
for each catagory where the gz files for that catagory are then extracted and placed
in a text file. The code will then randomly sample from k number of apk files
from each catagory passed in and will proceed to download the apks and convert to
smali code. This will take a bit of time as the functions are doing quite a websites

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

def getSitemap(url):

    '''
    A method that obtains all the gz files from the given url

    url - the sitemap url for apkpure
    '''

    url = requests.get(url).text
    soup = BeautifulSoup(url, 'lxml')

    li = []

    for elem in soup.find_all('loc'):
        li.append(elem.text)

    return li



def gzLinkSort(gzlist):

    '''
    A method that returns a dictionary of gz urls based on there catagory.
    the key represents the catagory and the values are a list of urls that
    fall under the given catagory


    gzlist - the list of gz files obtained from calling getSitemap
    '''


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




def findLocs(outFile, path):

    '''
    A method that goes through the xml files of the catagories found in the getGzCats
    method and stores all the links in a text file. These links are links that contain
    the page where we can download the apk files. This method is intended to be a
    helper method for getGzCats.

    outFile - the xml file of the catagory to be taken in. This will then be searched through
    to find the links coresponding to the download pages of the apk

    path - the location you want your xml files to be downloaded to

    '''

    file = open(outFile, 'r')
    line = file.readlines()

    locs = []
    for url in line:
        soup = BeautifulSoup(url, 'lxml')
        data = soup.find_all('loc')

        for i in data:
            locs.append(i.text)
    return locs



def getGzCats(gzDict, catagories, path):

    '''
    A method that takes in a dictionary (catagory (key), list of gz url (values))
    and the given catagories you wish to obtain the xml files of. The path specifies where
    the xml files will be downloaded. Do note that the xml files will be inserted into
    a directory with the corresponding name of the catagory

    gzDict - a dictionary containing the catagories of gz files and their assosiated links

    catagories - the catagories of gz files you want to obtain the xml files for

    path - the location you want your xml files to be downloaded to

    '''


    firstPart = 'https://apkpure.com/sitemaps/'
    os.chdir(path)

    for cat in catagories:

        os.chdir(path)

        if not os.path.exists(cat):
            os.makedirs(cat)

        newPath = path + str(cat)
        os.chdir(newPath)

        for file in gzDict[cat]:

            print(cat)
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


def random_sampler(filename, k):

    '''
    A method that randomly samples k number of apk urls from
    a specified filename (ex. comics_Links_APK.txt)

    filename - the specified txt file to sample from

    k - the numebr of samples you wish to obtain for a given
    catagory

    '''
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


    def getDownloadLinks(catagories, num, path):

    '''
    Get the link to the downloads page for apk on the main page.
    These links will direct us to the download page.

    num - specifies the number of links you wish to obtain

    catagories - A list of the catagories of apps you wish to call from

    path - the location you want your xml files to be downloaded to

    '''

    for cat in catagories:

        filename = str(cat) + '_Links_APK.txt'
        newPath = path + str(cat) + '/' + filename

        randomFiles = random_sampler(newPath, num)

        dLinks = []
        dic = {}

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
                print(err)
                pass


    return dLinks



    def downloadAPK(catagories, num, path):

    '''
    A method designed to get the links to download the APK of a given
    android app. These links will download the APK file when entered into
    the browser

    num - specifies the number of links you wish to obtain

    catagories - A list of the catagories of apps you wish to call from

    path - the location you want your xml files to be downloaded to

    **Current Limitations** - Some download links obtained from the getDownloadLinks
    method require the user to click on the download button and input a series of
    characters to continue with their download. This prevent some websites from being
    scrapped and the APK to be downloaded.
    '''


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
                print(err)
                pass



def getAPK(catagories, path):

    '''
    A method that gets the downloaded apk files from apkpure and
    stores them in their correct catagory directory in APK_Downloads.
    This method then converts the downloaded apk files into smali code
    and stores it in the current catagory directory

    catagories - A list of the catagories of apps you wish to call from

    path - the location you want your xml files to be downloaded to
    '''

    for cat in catagories:

        filename = str(cat) + '_Download_Links_APK.txt'
        newPath = path + str(cat) + '/' + filename
        catDir = path + str(cat)

        with open(newPath) as f:
            content = f.readlines()

        count = 0
        #nameList = getNames(strLocs, 10)

        for link in content:

            resp = requests.get(link, stream = True)
            contents = resp.content

            name = count

            out = os.path.join(catDir, str(cat) + '_' + str(name) +'.apk')
            #data = urllib2.urlopen(link).read()

            with open( out, "wb" ) as code:
                code.write(contents)
                os.chdir(catDir)
                os.system('apktool d ' + str(cat) + '_' + str(name) +'.apk')

            count += 1


def get_data(**kwargs):

    path = kwargs['path']
    catagories = kwargs['catagories']
    sampleSize = kwargs['sampleSize']

    gzlist = getSitemap('https://apkpure.com/sitemap.xml')
    catDicGz = gzLinkSort(gzlist)
    getGzCats(catDicGz, catagories, path)
    downloadAPK(catagories, sampleSize, path)
    getAPK(catagories, path)


if __name__== "__main__":
    # NOTE: the following line of code is specific to where data-params-apk.json has been downloaded to
    # os.chdir('/Users/kelkin/Documents/DSC_180A/APK_Downloads/')
    cfg = json.load(open('data-params-apk.json'))
    get_data(**cfg)
