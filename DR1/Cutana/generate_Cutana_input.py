# Copyright (c) European Space Agency, 2026.

# This file is subject to the terms and conditions defined in file `LICENSE.txt`, which is part of this source code package. No part of the package, including this file, may be copied, modified, propagated, or distributed except according to the terms contained in the file `LICENSE.txt`.


# importing necessary packages
from astroquery.esa.euclid.core import EuclidClass
import glob
import os
import pandas as pd


#choosing environment
Euclid = None
def set_env(envname, user = '', password = ''):
    global Euclid
    Euclid = EuclidClass(environment=envname)
    Euclid.login(user = user, password = password)
    

# Define functions

def chooseBestFile(df_res_dup):
    """Choosing best file for sources with multiple by checking where the source is closest to image centre"""
    
    min_dist_per_plotcode = df_res_dup.groupby(['right_ascension', 'filter_name'], as_index=False, sort=False)['dist'].idxmin()
    df_final = df_res_dup.loc[min_dist_per_plotcode["dist"]]
    return df_final

def addFilters(query, instrument_name, nisp_filters=[]):
    """In case nisp_filters is specified modify query to get files for only those filters"""
    filter_part = ""
    query_parts = query.split("ON ")
    for one_filter in nisp_filters:
        if one_filter != nisp_filters[-1]:
            filter_part += "(mosaics.filter_name='" + one_filter + "') OR "
        else:
            filter_part += "(mosaics.filter_name='" + one_filter + "')"
    query = query_parts[0] + "ON (" + filter_part + ") AND" + query_parts[1]
    return query

def addInstrument(query, instrument_name):
    if instrument_name == 'VIS' or instrument_name == 'NISP':
        query_parts = query.split("ON (")
        query = query_parts[0] + "ON (mosaics.instrument_name='" + instrument_name +"' AND " + query_parts[1]
    elif instrument_name == "":
        query_parts = query.split("ON (")
        query = query_parts[0] + "ON ((mosaics.instrument_name='VIS' OR mosaics.instrument_name='NISP') AND " + query_parts[1]
    else:
        raise ValueError('Incorrect value for parameter instrument_name:', instrument_name)
    return query

def checkInput(cutout_size, instrument_name, nisp_filters):
    """Checking user input value correctness for cutout_size, instrument name and nisp filters"""
    
    valid_cutout_sizes = ['pixel', 'arcsec']
    valid_instruments = ["", "VIS", "NISP"]
    valid_filters = ["NIR_H", "NIR_J", "NIR_Y", ""]
    if cutout_size not in valid_cutout_sizes:
        raise ValueError(f"Invalid cutout size. Choose from: {valid_cutout_sizes}")
    if instrument_name not in valid_instruments:
        raise ValueError(f"Invalid instrument name. Choose from: {valid_instruments}") 
    for filter_name in nisp_filters:
        if filter_name not in valid_filters:
            raise ValueError(f"Invalid filter name. Choose from: {valid_filters}") 
    if instrument_name=='VIS' and nisp_filters != []:
        raise ValueError(f"Invalid combination of input parameters. When instrument_name is VIS cannot specify nisp_filters")
    return

def generateCutanaInputFile(source_query, instrument_name="", nisp_filters=[], cutout_size='pixel', cutout_size_value=50, output_filepath = '/media/user/example_notebook_outputs/cutana_input.csv', drop_noncutana_cols=True):
    """Match sources with mosaic files by checking if source coordinates are in mosaic file fov or 
    if file tile_index matches the first 9 digits of source's segmentation_map_id"""
    
    #check input correctness
    checkInput(cutout_size, instrument_name, nisp_filters)
    
    shortcut = False
    query= f"""SELECT 'TILE_'||CAST(mosaics.tile_index AS CHAR(25))||'_'||CAST(sources.right_ascension AS CHAR(25)) as SourceID, sources.right_ascension, sources.declination, mosaics.datalabs_path||'/'||mosaics.file_name as fits_file_paths, mosaics.filter_name, DISTANCE(mosaics.ra, mosaics.dec, sources.right_ascension, sources.declination) AS dist
                FROM {source_query} as sources
                JOIN dr1.mosaic_product AS mosaics
                ON (mosaics.fov IS NOT NULL AND CONTAINS(CIRCLE(sources.right_ascension, sources.declination, {0.5/60}), mosaics.fov)=1)
                WHERE mosaics.datalabs_path IS NOT NULL
                ORDER BY sources.right_ascension ASC"""
    print(query)
    
    #check if column names contain segmenation_map_id and object_id for shortcut 
    if 'user' in source_query:
        all_colnames = [col.name for col in Euclid.load_table(table=source_query, verbose=False).columns]
    else:
        all_colnames = source_query
        
    if 'segmentation_map_id' in all_colnames:
        # print('SHORTCUT')
        shortcut=True
        query= f"""SELECT 'TILE_'||SUBSTRING(CAST(segmentation_map_id AS CHAR(25)), 1, 9)||'_'||CAST(sources.right_ascension AS CHAR(25)) as SourceID, sources.right_ascension, sources.declination, mosaics.datalabs_path||'/'||mosaics.file_name as fits_file_paths, mosaics.filter_name
            FROM {source_query} as sources
            JOIN mosaic_product AS mosaics
            ON (CAST(mosaics.tile_index AS CHAR(25)) = SUBSTRING(CAST(segmentation_map_id AS CHAR(25)), 1, 9))
            WHERE mosaics.datalabs_path IS NOT NULL
            ORDER BY sources.right_ascension ASC"""

    #modify query to include instrument selection
    query = addInstrument(query, instrument_name)
    
    #modify query to include only the provided nisp filters
    if len(nisp_filters) > 0 and len(nisp_filters) < 3:
        query = addFilters(query, instrument_name, nisp_filters)
    
    #make query to get file info
    job = Euclid.launch_job_async(query, verbose=False)
    if job == None:
        raise AttributeError("Query for files failed. Please make sure your source query or user table contains columns named 'right_ascension' and 'declination' or 'ra' and 'dec'. When using a source query it should have brackets around it.")
    df_res = job.get_results().to_pandas()
    
    #choose best mosaic
    if shortcut == False:
        df_res = chooseBestFile(df_res)
        
    df_res = df_res.replace({'SourceID': {'\.': ''}}, regex=True)
    df_res = df_res.groupby(list(df_res)[:list(df_res).index('fits_file_paths')])['fits_file_paths'].apply(lambda grp: list(set(grp))).reset_index()
    print("Found", len(df_res), "query results")
    
    #add constant diameter
    df_res.insert(loc=3, column='diameter_'+cutout_size, value=cutout_size_value)
    
    #convert list of file_paths to str
    df_res = df_res.astype({"fits_file_paths": str})
    
    #add user columns back if requested
    if drop_noncutana_cols == False:
        query_user_table = f"""SELECT * FROM {source_query} as sources"""
        job = Euclid.launch_job_async(query_user_table, verbose=False)
        df_user_table = job.get_results().to_pandas()
        df_res = pd.merge(df_res, df_user_table, on=['right_ascension', 'declination'], how='outer')
    
    #rename cols to fit cutana
    df_res = df_res.rename(columns={'right_ascension': 'RA', 'declination': 'Dec'})
    
    #save to csv file for cutana
    df_res.to_csv(output_filepath, index=False)
    print('Creating Cutana compatible input file at', output_filepath)
    
    return df_res