# Processing Satelite Imagery from Planet Labs

Showcasing a workflow consisting of multiple python scripts to help download imagery using the Planet Labs APIs. I recorded a video to display a tutorial and showcase time saved while using this workflow. 

## Authors

The following code was created by [Aidan Hayes](https://github.com/aphayes2025) and [Harrison Myers](https://github.com/finnmyers96/finnmyers96). 

## Setup and running [api.py](https://github.com/aphayes2025/workflow-processing-planet-labs/blob/main/api.py)

1. download requirements via `requirements.txt` for pip installs. 
2. Create a .env file. Inside should be the following variables: API_KEY (api key corresponding to your planet labs account), DIR_PATH (path to folder containing shapefiles). NOTE: May need to change getPolygons() inside api.py to fit your shapefiles. 
3. Look inside api.py, there are 3 functions that return parameters for the different planet labs apis (stat search, quick search and orders). Change the filters within these functions as you need to meet your requirements for your imagery. The following variables will most likely need to be swapped inside main: START_TIME, order_name.
4. run api.py this will automatically run the stats search api and will print out each site's amount of imagery. It will then prompt you if you want to order them. After confirmation from user, the script will loop through all the given sites and order them given the order name. Depending on the number of imagery you have, it may need to make two orders (there is a limit of 500 imagery per order). 


## Overview of Helper Scripts
There are additional scripts to help with processing the satelite imagery. 
1. First [unzip.py]() contains two functions, unzip_file() unzips a file (one of the format that planet labs packages their orders in) and rewrite_files() (which takes the unzipped file and looks for a specific subset of the order, like .tif images or .json files and puts them in a new folder.
