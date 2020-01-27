# DSC_180A

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
