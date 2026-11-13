#   Copyright (c) European Space Agency, 2026.
#
#   This file is subject to the terms and conditions defined in file 'LICENSE.txt', which
#   is part of this source code package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file 'LICENSE.txt'.


from astropy.io import fits
import pandas as pd
from concurrent.futures import ProcessPoolExecutor


def chunk_gen(lst, n):
    ""
    "Split an input list into multiple chunks of size =< n"
    ""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        

def check_inp_table(astropy_table):
    ""
    "Verifies tha the input table contains the necessary fields, and generates full path to fits files"
    ""
    base_keys = ['hdu_index', 'source_id', 'ra_obj', 'dec_obj']
    keys      = astropy_table.keys()
    
    for base_key in base_keys:
        try:
            index = keys.index(base_key)  # Raises ValueError if not found
        except ValueError:
            print(f"Error: '{base_key}' not found in the list.")

    astropy_table['fits_path'] = [astropy_table['datalabs_path'][ii] + '/' + astropy_table['file_name'][ii] for ii in range(len(astropy_table))]    
    return astropy_table


def make_chunks(astropy_table, chunk_size):
    ""
    "Split an input list into multiple chunks of size =< n"
    ""
    astropy_table = check_inp_table(astropy_table)
    chunks        = list(chunk_gen(astropy_table, chunk_size))

    if len(chunks[0]) == len(chunks[-1]):
        print(f'* Input table with {len(astropy_table)} rows is split into {len(chunks)} chunks of {chunk_size} each.')
    else:
        print(f'* Input table with {len(astropy_table)} rows is split into {len(chunks)} chunks of {chunk_size} each (except for the last chunk that contains {len(chunks[-1])} elements).')     
    
    return chunks


def read_base(path, hdu_i, source_id, ra_obj, dec_obj):
    ""
    "Reads Euclid (SIR) MEF file and extract selected HDU. It also adds source_id, ra, and dec to the returned HDU header."
    ""
    with fits.open(path, memmap=True) as hdul:
        hdu = hdul[hdu_i]
        data = hdu.data
        hdu.header['SOURC_ID'] = (source_id, 'spectra_source table source_id')
        hdu.header['RA_OBJ']   = (ra_obj,    'spectra_source table R.A. [deg]')
        hdu.header['DEC_OBJ']  = (dec_obj,   'spectra_source table Declination[deg]')        
    return data, hdu.header


def create_mef(chunk, output_file = 'mef_file.fits'):
    ""
    "Reads chunk (Astropy table) and generates Multi Extension Fits (MEF) file and temporal metadata table using parallelisation"
    ""

    fits_path = list(chunk['fits_path'])
    hdu_index = list(chunk['hdu_index'])
    source_id = list(chunk['source_id'])
    ra        = list(chunk['ra_obj'])
    dec       = list(chunk['dec_obj'])

    # MEF generation ===================
    with ProcessPoolExecutor() as ex:
        results = list(ex.map(read_base, fits_path, hdu_index, source_id, ra, dec))

    primary_hdu = fits.PrimaryHDU()
    hdul_new    = fits.HDUList([primary_hdu])
    for ii in range(len(results)):
        table_hdu = fits.BinTableHDU(data=results[ii][0], header=results[ii][1])
        hdul_new.append(table_hdu)

    # Metadata =========================
    df              = pd.DataFrame.from_dict({'source_id':source_id, 'ra':ra, 'dec':dec, 'fits_file':output_file})
    df['hdu_index'] = [inp + 1 for inp in df.index]

    return df, hdul_new



def create_mef_files(chunks, output_folder = './', verbose = True, metadata_table = 'metadata_table.csv'):
    ""
    "Reads chunk (Astropy table) and generates MEF file and temporal metadata table"
    ""

    metadata_out = output_folder + metadata_table
    chunk_id     = -1
    df_list      = []

    for chunk in chunks:
        chunk_id     = chunk_id + 1
        output_file  = f"{output_folder}chunk_{chunk_id}.fits"
        df, hdul_new = create_mef(chunk, output_file = output_file)

        df_list.append(df)
        hdul_new.writeto(output_file, overwrite=True)
        if verbose:
            print(f'* Chunk: {chunk_id:4.0f} stored as: {output_file:>60s} - It contains {len(hdul_new)-1} spectra + 1 primary HDU')

    if verbose:
        print(f'* Metadata table stored as: {metadata_out}')

    metadata     = pd.concat(df_list).reset_index(drop = True)
    metadata.to_csv(metadata_out)
    return metadata
