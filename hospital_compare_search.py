#!/usr/bin/env python
__author__ = 'caroline wester'
# Coding exercise for Radial Analytics
# Project:  The Centers for Medicare and Medicaid Services (CMS) releases Hospital Compare datasets for acute inpatient
# hospitals on a quarterly cycle.  Included in these datasets are administrative information, quality information, and
# financial information for roughly 4,800 hospitals.
#
# The aim of this project is to create a simple command-line search interface into the Hospital Compare dataset that
# allows a user to generate a list of ranked facilities by searching by geographic and/or other facility characteristics

#imported packages
import argparse
import re
import sys
import simplejson
from haversine import haversine
import pandas as pd
from pandas import *
import logging

#  Logging function is used to setup a log file when user adds the verbose flag.
def init_logging(filename):
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # create a file handler
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)

    logger.info('Begin logging')


# validate_zip_code will check to make sure a valid 5 digit zipcode has been entered.  If the zip code is incorrect,
#    the program will end.
def validate_zip_code(zip_code):
    correct_zip_code = re.compile("^\d{5}(?:[-\s]\d{4})?$")

    if correct_zip_code.match(zip_code):
        return (zip_code)
    else:
        return (-1)


# parse_input will parse through the entered inputs as follows:
# Arguments should be:
#       zip_code (required),
#       num_facilities (Optional, default = 20),
#       min_overall_rating (Opt, default = none)

def parse_input(args):
    parser = argparse.ArgumentParser(
        description='A simple command-line search interface into Hospital Compare dataset that allows a user to generate'
                    ' a list of ranked facilities by searching by geographic and/or other facility characteristics'
    )
    parser.add_argument('-z', '--zip_code', help='Required:  Enter a 5 digit zip code that geographically anchors the '
                        'search.', required=True)
    parser.add_argument('-nf', '--num_facilities', help='Optional(default:20):  The maximum number of facilities '
                        'returned by the search', default=20,type=int)
    parser.add_argument('-mor', '--min_overall_rating', help='Optional (default:no restriction):  The minimum allowable'
                        ' quality rating for each hospital returned',default=-1, type=float)
    parser.add_argument('-v', '--verbose', help='Increase output verbosity and log information', action='store_true')
    my_args = parser.parse_args()

    if my_args.verbose:
        logger.info('verbose flag is set')

    if validate_zip_code(my_args.zip_code) == -1:
        parser.error('Zip code must be five digits.')
    else:
        logger.info('zip code is valid')
        anchor_zip_code = my_args.zip_code

    if my_args.num_facilities:
        logger.info('Number of Facilities being returned: %s ', my_args.num_facilities)

    if my_args.min_overall_rating:
        logger.info('Overall Rating being used: %s', my_args.min_overall_rating)
    return my_args

# Main program
def main(args):
    # Initialize logging to be used if verbose flag is set
    init_logging('./logs/hospital_compare_search.log')

    # Read arguments and ensure they meet the requirements
    my_args = parse_input(args)

    # create datasets for each of the input files being used.
    logger.info('Creating datasets')
    hospitals_dataset = pd.read_csv('./inputs/Hospital_General_Information.csv', dtype={'ZIP Code': str})
    spending_dataset = pd.read_csv('./inputs/Medicare_Hospital Spending_per_Patient_Hospital.csv',
                                   dtype={'ZIP Code': str})
    zip_codes_dataset = pd.read_csv('./inputs/zipcodecentroids.csv', dtype={'zip_code': str})

    # Using the zipcodecentroids.csv file, find the anchor point using the passed zip code
    zip_codes_df = DataFrame(zip_codes_dataset)

    anchor_zip_code = my_args.zip_code
    logger.info('Zip code passed and being used as anchor:  %s', anchor_zip_code)   #zip code passed

    anchor_result = zip_codes_df.loc[zip_codes_df['zip_code'] == anchor_zip_code]

    anchor_lat = anchor_result['lat']
    anchor_lng = anchor_result['lng']
    anchor = (anchor_lat, anchor_lng)

    #create a new dataframe for the distance
    hospital_distance_df = DataFrame([{'zip_code':'', 'lat': '', 'lng':'','distance':''}])
    hospital_distance_df = hospital_distance_df[['zip_code','lat', 'lng','distance']]

    new_record_set = []
    # Create a new dataframe with the zip code and the distance from anchor for each of the hospitals
    for i in zip_codes_dataset.itertuples():
        # Use haversine, for each row in the dataset, find the distance
        hospital_zipcode = getattr(i,'zip_code')
        hospital_lat = getattr(i,'lat')
        hospital_lng = getattr(i,'lng')
        hospital_location = (hospital_lat, hospital_lng)
        hospital_distance_to_anchor = haversine(anchor, hospital_location)

        # Add a row to the new_record_set)
        new_record={'zip_code':hospital_zipcode, 'lat': hospital_lat, 'lng': hospital_lng,
                    'distance':hospital_distance_to_anchor}
        new_record_set.append(new_record)

    hospital_distance_df = DataFrame(new_record_set)

    # Merge all datasets together
    merged_data = hospitals_dataset.merge(spending_dataset, on='Provider ID')
    merged_data2 = merged_data.merge(hospital_distance_df, left_on='ZIP Code_x', right_on='zip_code')
    #logger.info(merged_data2)

    # Using the fully merged data, select subset from the query

    df = DataFrame(merged_data2)
    df_filtered = df[df['Hospital overall rating'] >= my_args.min_overall_rating]
    sorted_df = df_filtered.sort_values(by=['Hospital overall rating','distance', 'Hospital Name_x'],
                                        ascending = [False, True, True]).head(my_args.num_facilities)

    # logger.info(sorted_df[['Hospital overall rating','distance','Hospital Name_x' ]])
    logger.info(sorted_df)

    json_output_raw = sorted_df[['Provider ID', 'Hospital Name_x', 'Address_x', 'City_x', 'State_x', 'ZIP Code_x',
                                 'Hospital overall rating','Score', 'lat', 'lng', 'distance']].to_json(orient='records')
    json_output = simplejson.loads(json_output_raw)
    print (simplejson.dumps(json_output, indent=4, sort_keys=True))

    return json_output


if __name__ == "__main__":
    sys.exit(not main(sys.argv))
