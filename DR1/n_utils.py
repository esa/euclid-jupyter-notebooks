#   Copyright (c) European Space Agency, 2026.
#
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this source code package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file 'LICENCE.txt'.


from astropy.io import fits
from astropy.visualization import simple_norm, astropy_mpl_style, ImageNormalize, PercentileInterval, AsinhStretch, LogStretch
import matplotlib.pyplot as plt
import time

def get_query_results(EuclidObj, query, display_rows = -1, display_table = True, output_format = 'votable'):
    ""
    "Display ADQL query and first results"
    ""
    print(f'ADQL query: ')
    print(query)
    print()
    start = time.time()
    job = EuclidObj.launch_job_async(query, output_format = output_format)
    res = job.get_results()
    
    end = time.time()
    print(f"Total runtime: {end - start:3.1f} seconds")
    
    if display_rows == -1:
        dset = res
    else:
        dset = res[0:display_rows]
        print(f'* Job output contains {len(res)} rows; displaying first {display_rows} rows: ')
    if display_table:
        display(dset)
    return res


def make_canvas(xlabel = "", ylabel = "", fontsize = 16, legend = True):
    ""
    "Generic Canvas maker"
    ""
    plt.xlabel(xlabel, fontsize = fontsize)
    plt.ylabel(ylabel, fontsize = fontsize)
    plt.xticks(fontsize = fontsize)
    plt.yticks(fontsize = fontsize)
    if legend:
        plt.legend(fontsize = fontsize * 0.8)


def plot_image(fits_path = '', under_samp = 10, cmap = 'viridis', norm_pc = 99.5, verbose = True, cbar = True):
    """
    Reads a single-HDU file and plots an image, or an undersampled version of the image, or a cutout.
    """
    if verbose:
        print(f'FITS file path: {fits_path}')
        if under_samp !=0:
            print(f'Note: The displayed image is undersampled by a {under_samp} factor to speed up')
        print()

    # loading image data from FITS file ========
    with fits.open(fits_path) as hdul:
        img_data = hdul[0].data
        img_head = hdul[0].header

    # Plotting =================================
    if under_samp != None:
        img_data_u = img_data[::under_samp, ::under_samp] # Undersampled image
    else:
        img_data_u = img_data
    plt.imshow(img_data_u, cmap=cmap, origin='lower', norm=ImageNormalize(img_data_u, interval=PercentileInterval(norm_pc), stretch=AsinhStretch()))
    if cbar:
        cbar = plt.colorbar()
        cbar.set_label(img_head['BUNIT'])
    _ = plt.axis('off')
    
    return img_data, img_head


def plot_image(fits_path,under_samp=10,cmap="viridis",norm_pc=99.5,verbose=True,cbar=True):
    """
    Read a FITS image and display it.

    Parameters
    ----------
    fits_path : str
        Path to the FITS file.
    under_samp : int or None, optional
        Display every Nth pixel along each axis. Set to None or 1
        to display the full-resolution image.
    cmap : str, optional
        Matplotlib colormap.
    norm_pc : float, optional
        Percentile used for image normalisation.
    verbose : bool, optional
        Print information about the file and display settings.
    cbar : bool, optional
        Add a colour bar to the plot.

    Returns
    -------
    tuple
        (img_data, img_head)
    """

    if verbose:
        print(f"FITS file: {fits_path}")
        if under_samp not in (None, 1):
            print(
                f"Note: displaying an image undersampled by a factor "
                f"of {under_samp} for faster rendering."
            )
        print()

    # Load image data
    with fits.open(fits_path) as hdul:
        img_data = hdul[0].data
        img_head = hdul[0].header

    # Apply undersampling if requested
    if under_samp > 1:
        img_display = img_data[::under_samp, ::under_samp]
    else:
        img_display = img_data

    # Display image
    plt.imshow(img_display,cmap=cmap,origin="lower",
        norm=ImageNormalize(img_display,interval=PercentileInterval(norm_pc),
            stretch=AsinhStretch()))

    if cbar:
        cb = plt.colorbar()
        if "BUNIT" in img_head:
            cb.set_label(img_head["BUNIT"])

    plt.axis("off")

    return img_data, img_head


def plot_cutouts(list_cutout,figsize=(10, 7),cmap="viridis",norm_pc=99.5,verbose=True,n_cols=3,n_rows=1,titles=None):
    """
    Display a gallery of image cutouts.

    Parameters
    ----------
    list_cutout : list
        List of Cutout2D objects (or objects with a .data attribute).
    figsize : tuple, optional
        Figure size in inches.
    cmap : str, optional
        Matplotlib colormap.
    norm_pc : float, optional
        Percentile used for image normalisation.
    verbose : bool, optional
        Print basic information about the gallery.
    n_cols : int, optional
        Number of columns in the subplot grid.
    n_rows : int, optional
        Number of rows in the subplot grid.
    titles : list of str, optional
        Titles for each cutout.
    """

    if verbose:
        print(f"Displaying {len(list_cutout)} cutout(s)")

    fig, axes = plt.subplots(n_rows,n_cols,figsize=figsize,squeeze=False)

    axes = axes.ravel()

    for ii, (ax, cutout) in enumerate(zip(axes, list_cutout)):

        ax.imshow(cutout.data,cmap=cmap,origin="lower",
            norm=ImageNormalize(cutout.data,interval=PercentileInterval(norm_pc),
                stretch=AsinhStretch()))
        ax.axis("off")
        if titles is not None and ii < len(titles):
            ax.set_title(titles[ii])

    plt.tight_layout()
    plt.show()

    return fig, axes