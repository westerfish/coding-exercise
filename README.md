# Coding-exercise
Within this repo, I have added a python script called hospital_compcare_search. Please run this from the command line, use the -h option to get more details on the input requirements.

## Example:_  ./hospital_compare_search.py -z 01742 -nf 10 -mor 1 -v

## Execution: 
* The code can be run from the terminal of an Ubuntu or macOS/OSX machine. 
* Inputs are specified via command-line arguments (e.g., see the argparse python parser). 
* Outputs are printed directly to standard output (the console) in properly-formatted JSON, where they can be redirected to a .json file.
* Code execution instructions are documented.

## Inputs: 
* The following input arguments can be passed to the interface: 
* -z or --zip_code – required. The five-digit zip code that geographically anchors the search. 
* -nf or --num_facilities – optional (default: 20). The maximum number of facilities returned by the search. 
* -mor or --min_overall_rating – optional (default: no restriction). The minimum allowable overall quality rating for each returned hospital. The overall rating for each hospital is listed in the “Hospital General Information” file.

## Outputs: 
* Outputs should be returned as a properly-formatted human-readable JSON list of hospital dicts. The keys for each hospital dict should be as follows:

* ccn – unique Provider ID (the CMS Certification Number [CCN]) from the “Hospital General Information” file. 
* name – hospital name from the “Hospital General Information” file. 
* address – full address consisting of street, city, state and zip code from the “Hospital General Information” file. 
* overall_rating - overall rating (1-5 or null) from the “Hospital General Information” file. 
* spending_score – normalized hospital spending per patient from the “Score” field of the “Medicare Hospital Spending per Patient” file (float or null) 
* lat – latitude of the hospital zip code centroid
* lng – longitude of the hospital zip code centroid o distance_miles – distance in miles from the centroid of the search zip code centroid to the hospital zip code centroid 

## Details
The output list should be sorted first by descending order of overall_rating, second by ascending order of distance_miles, and third by name. 
### Geographic search: 
* To simplify distance calculations between the geographic anchor and each hospital, we are including a “zip_code_centroids.csv.gz” file that reports the centroid lat and lng for all zip codes in the United States. 
* To calculate the distance in miles between the input zip_code and each hospital, simply calculate the distance between the input zip code and hospital zip code centroids- there is no need to geocode any hospital addresses. 
* To implement a distance calculation between two (lat, lng) pairs, you will find the haversine formula and/or the “haversine” python package to be quite useful.
