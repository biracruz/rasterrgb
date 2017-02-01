# -*- coding: utf-8 -*-
from rasterrgb import *

def calculate_luminance(rgb):
    """ Calculates the L value on luminance function.
    
    L = 0.2126*R + 0.7152*G + 0.0722*R   
    
    Note:
       See more at https://en.wikipedia.org/wiki/Relative_luminance
    
    Args:
        rgb (list): 3 color values [r, g, b]
    
    Returns:
        numpy.float64: the calculated luminance
    
    """
    L = np.array([0.2126, 0.7152, 0.0722])
    return  np.sum(np.array(rgb)*L)


def luminance_difference(rgb, rgb_to_compare):
    """ Just the difeerence between 2 calculated luminances
    
    Args:
        rgb (list): 3 color values [r, g, b]
        rgb_to_compare: 3 color values [r, g, b]
    
    Returns:
        numpy.float64: the calculated difference luminance
    
    """
    return calculate_luminance(rgb_to_compare) - calculate_luminance(rgb)


def luminance_ratio(rgb, rgb_to_compare):
    """ The ratio between 2 calculated luminances
    
    Args:
        rgb (list): 3 color values [r, g, b]
        rgb_to_compare (list): 3 color values [r, g, b]
    
    Returns:
        numpy.float64: the calculated ratio luminance
    
    """
    return calculate_luminance(rgb) / calculate_luminance(rgb_to_compare)   


def _add_with_limits(x_array, factor):
    """ Takes an array and sum with the factor with 255 and 0 bounds.
    
    Args:
        x_array (np.array): a list with range 0 to 255
        factor (int): the value to be added 
    
    Returns:
        numpy.array: an array with each value added by the factor
    
    """
    y = []
    for _x in x_array:
        s = _x + factor
        if s > 255:
            y.append(255)
        elif s < 0:
            y.append(0)
        else:
            y.append(s)
    return np.array(y)


def calculate_brightness_functions(bands_medians, ref_bands_medians, no_data_value=0):            
    """ Calculates the brightness adjustment functions for two average or median of two images.
    
    Args:
        bands_medians (list): 3 color  medians values [r, g, b] to be adjusted
        ref_bands_medians (list): 3 color medians reference values [r, g, b]
    
    Returns:
        list: list of scipy interpolate functions whose calls methods uses
        interpolation to find the value of new points.
    
    """
    factor = luminance_difference(bands_medians, ref_bands_medians)              
    print "\n Calculated Brightness Difference:"+str(factor)
    x = np.arange(0, 256)
    y = _add_with_limits(x, factor)
    f = interpolate.interp1d(x, y)
    transFunc = [ f for b in range(3)]
    return transFunc