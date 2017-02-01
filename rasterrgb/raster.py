# -*- coding: utf-8 -*-
import sys
import os
import brightness, color, stats
from rasterrgb import *


class Raster(object):
    """ A class to facilitate raster tiff manipulation and adjustments using gdal functions.
    
    Most important methods are publics and destinated to color balancing 
    and brightness adjustment of images producing 3 bands only output images.

    Attributes
    ----------
        name (str): file name of original image
        out_path (str): path where outputs will be saved
        rasterRGB (dict): dictionary containing Gdal img and bands objects
        luminance (float): the luminance calculated value of original image
        R (list): the values of the Red band on each pixel of image
        R_median: median value of the Red band
        G (list): the values of the Green band on each pixel of image
        G_median: median value of the Green band
        B (list): the values of the Blue band on each pixel of image
        B_median: median value of the Blue band

    """
    def __init__(self, name, out_path):
        self.name =  os.path.basename(name)
        self.out_path = out_path
        self.rasterRGB = None
        self._read_raster_img(name)
        self.luminance = None                
        self.R = None
        self.R_median = None        
        self.G = None
        self.G_median = None 
        self.B = None
        self.B_median = None


    def _read_raster_img(self, file_name):
        """ Read the image file to img and bands objects. """      
        _img =  gdal.Open(file_name)
        _bands = [_img.GetRasterBand(b+1) for b in range(3)]
        self.rasterRGB = {"img": _img, "bands": _bands }


    def _generate_luminance(self):
        """ Calculates the luminance for the readed image."""
        medians =  stats.calculate_medians(self.rasterRGB["bands"])  
        self.luminance = brightness.calculate_luminance(medians)
    

    def _generate_medians(self):
        """ Calculates the medians values for each band of the readed image."""
        medians =stats.calculate_medians_ignore_dark(self.rasterRGB["bands"])
        self.R_median = medians[0]
        self.G_median = medians[1]
        self.B_median = medians[2]


    def _generate_bands_arrays(self):
        """ Read the Gdal bands as array for the class. """
        self.R = self.rasterRGB["bands"][0].ReadAsArray()
        self.G = self.rasterRGB["bands"][1].ReadAsArray()
        self.B = self.rasterRGB["bands"][2].ReadAsArray()


    def _generate_output_img(self, output_name):
        """ Generates an output 8 bits GTiff image based on the 
        original image read."""
        inIMG = self.rasterRGB["img"]
        driver = gdal.GetDriverByName('GTiff')
        dest_img = driver.Create(output_name, 
                                 inIMG.RasterXSize, 
                                 inIMG.RasterYSize, 
                                 3, 
                                 gdal.gdalconst.GDT_Byte)
        dest_img.SetGeoTransform(inIMG.GetGeoTransform())
        dest_img.SetProjection(inIMG.GetProjection())
        return dest_img         
    

    def _file_name(self, prefix, out_path, out_file_name):
        """ Prepare the name of a file using prefix, path, and output name."""
        out_name = prefix+os.path.basename(out_file_name)
        return  os.path.join(out_path,out_name)
    
    
    def _create_image_with_functions(self, functionsRGB, _file_name, no_data_value):            
        """ Create a new original based image adjusted with linear interpolation functions.    
        Args:
            functionsRGB (list): for each band there is a list of scipy interpolate functions whose calls methods uses
        interpolation to find the value of new points. 
        """
        inIMG = self.rasterRGB["img"]        
        dest_img = self._generate_output_img(_file_name)        
        
        if self.R == None or self.G == None or self.R == None:
            self._generate_bands_arrays()    

        type_array = type(self.R[0][0])
        for l in range(inIMG.RasterYSize):            
            print("line "+str(l+1)+" of "+ str(inIMG.RasterYSize)+" \r")
            #separate no data pixels
            r_no_data_ixs = np.where(self.R[l] == no_data_value)    
            g_no_data_ixs = np.where(self.G[l] == no_data_value)
            b_no_data_ixs = np.where(self.B[l] == no_data_value)
            #save the positions where pixels contains no data in 3 bands  
            positions = np.intersect1d(r_no_data_ixs, g_no_data_ixs, b_no_data_ixs)
            # delete positions from lines
            r_line = np.delete(self.R[l], positions, 0)
            g_line = np.delete(self.G[l], positions, 0)
            b_line = np.delete(self.B[l], positions, 0)        
            if len(r_line) == 0 and len(g_line) == 0 and len(b_line) == 0:                
                #all pixels were deleted
                continue
            else:           
                #apply hist2sd 
                _r_saida = functionsRGB[0](r_line).astype(type_array)
                _g_saida = functionsRGB[1](g_line).astype(type_array)
                _b_saida = functionsRGB[2](b_line).astype(type_array)    
                #insert processed values on original line
                np.place(self.R[l], self.R[l] > no_data_value, _r_saida)
                np.place(self.G[l], self.G[l] > no_data_value, _g_saida)
                np.place(self.B[l], self.B[l] > no_data_value, _b_saida)
        print("\n Writing raster ...")
        print("Band 1 ...")
        dest_img.GetRasterBand(1).WriteArray(self.R)
        print("Band 2 ...")
        dest_img.GetRasterBand(2).WriteArray(self.G)
        print("Band 3 ...")
        dest_img.GetRasterBand(3).WriteArray(self.B)


    def adjust_colors(self, no_data_value = 0): 
        """ Creates a new 8 bits image using histogram 2sd color balance. """       
        transfFunc = color.calculate_color_balance_functions(self.rasterRGB['bands'])
        generated_file_name = self._file_name("8bit_hist2sd_", self.out_path, self.name)
        self._create_image_with_functions(transfFunc, generated_file_name, no_data_value)
        return generated_file_name


    def adjust_remove_border(self):
        """ Creates a new image removing border (using value = 0). """                
        generated_file_name = self._file_name("no_border_", self.out_path, self.name)
        inIMG = self.rasterRGB['img']
        gdal.Translate(generated_file_name, inIMG, noData = 0)
        return generated_file_name
    

    def adjust_brightness(self, ref_bands_medians, no_data_value=0):
        """ Creates a new brightness adjusted image using a reference."""
        self._generate_medians()
        bands_medians = [self.R_median, self.G_median, self.B_median]
        transfFunc = brightness.calculate_brightness_functions(bands_medians,
                                                   ref_bands_medians)
        generated_file_name = self._file_name("brightness_", self.out_path, self.name)
        self._create_image_with_functions(transfFunc, generated_file_name, no_data_value)
        return generated_file_name

    

 