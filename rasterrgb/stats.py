# -*- coding: utf-8 -*-
from rasterrgb import *

def calculate_stats(gdal_raster_bands):
    """ Basic statistics of bands

    Calculates Min, Max, Mean, Standar Deviation, Median 
    and Percentiles (25, 75, 95) for each band of the raster.

    Note:
        This function needs a refactoring for a better return object.
    
    Args:
        raster_bands (list): 3 GDALRasterBand.
    
    Returns:
        list: list of list with values for each band. MinMax and MeanSd 
            are tuples, so to access Max it's necessary to get 
            stats[<band index>]['MinMax'][1].

    """
    bands_stats = []
    for band in gdal_raster_bands:
        stats = {}
        stats["MinMax"] = band.ComputeRasterMinMax()
        stats["MeanSd"] = band.ComputeBandStats()
        np_array = band.ReadAsArray()
        stats["Median"] = np.median(np_array)
        stats["P25"] = np.percentile(np_array, 25)
        stats["P75"] = np.percentile(np_array, 75)
        stats["P95"] = np.percentile(np_array, 95)
        bands_stats.append(stats)
    return bands_stats


def calculate_means(gdal_raster_bands):
    """ Calculates the average of the image bands.

    Note:
        The use of this function for luminance calculation is not recommended.
    
    Args:
        raster_bands (list): 3 GDALRasterBand.
    
    Returns:
        list: list of averages for each band.

    """
    means = []
    for band in gdal_raster_bands:
        np_array = band.ReadAsArray()
        means.append(np.mean(np_array))
    return means


def calculate_medians(gdal_raster_bands):
    """ Calculates the median of the image bands.

    Note:
        This function is recommended for luminance calculation. 
    
    Args:
        raster_bands (list): 3 GDALRasterBand.
    
    Returns:
        list: list of medians for each band.

    """
    medians = []
    for band in gdal_raster_bands:
        np_array = band.ReadAsArray()
        medians.append(np.median(np_array))
    return medians


def calculate_medians_ignore_dark(gdal_raster_bands):
    """ Calculates the median of the image bands.

    Calculates the midian ignoring values of band bellow than 5.
    
    Note:
        This function is recommended for luminance calculation. 
    
    Args:
        raster_bands (list): 3 GDALRasterBand.
    
    Returns:
        list: list of medians for each band.
        
    """
    medians = []
    for band in gdal_raster_bands:
        np_array = band.ReadAsArray()
        ignore_np_array = np.ma.masked_outside(np_array, 5, 255).compressed()
        medians.append(np.median(ignore_np_array))
    return medians