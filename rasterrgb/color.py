# -*- coding: utf-8 -*-
from rasterrgb import *


def calculate_color_balance_functions(raster_bands, no_data_value=0):
    """ 
    Calculates the color balance adjustment functions for gdal raster bands 
    applying a mean +-2SD histogram stretch to images and converting to 8bit.
    
    Notes:
        This part comes from http://gis.stackexchange.com/a/100097,
        with all the credits to the great Daniel (daniel.victoria@gmail.com)
    
    Args:
        raster_bands (list): 3 GDALRasterBand, each band can be readed as an array.
    
    Returns:
        list: list of scipy interpolate functions whose calls methods uses
        interpolation to find the value of new points.
    
    """
    minMax = []
    meanSD = []
    for b in raster_bands:    
        minMax.append(b.ComputeRasterMinMax())
        meanSD.append(b.ComputeBandStats())        
    bandVals = [[0, max(minMax[b][0], meanSD[b][0] - 2* meanSD[b][1]),
                 min(minMax[b][1], meanSD[b][0] + 2*meanSD[b][1]), 65536] for b in range(3)]                         
    transfVals = [1,2, 254, 255]
    return [interpolate.interp1d(bandVals[b], transfVals) for b in range(3)] 