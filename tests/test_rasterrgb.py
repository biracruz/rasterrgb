#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_rasterrgb
----------------------------------
Tests for `rasterrgb` module.
"""


import sys, os
import unittest
from rasterrgb import raster 
import numpy as np
import gdal, ogr, osr

class TestRaster(unittest.TestCase):

    TEST_FILE = "test.tif"
    rrgb = None

    def array2raster(self, newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array):
        """ this probably can go to another class. """
        cols = array.shape[1]
        rows = array.shape[0]
        originX = rasterOrigin[0]
        originY = rasterOrigin[1]
        driver = gdal.GetDriverByName('GTiff')
        outRaster = driver.Create(newRasterfn, cols, rows, 3, gdal.GDT_Byte)
        outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
        outband = outRaster.GetRasterBand(1)
        outband.WriteArray(array)
        outband = outRaster.GetRasterBand(2)
        outband.WriteArray(array)
        outband = outRaster.GetRasterBand(3)
        outband.WriteArray(array)
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(4326)
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
        outband.FlushCache()


    def setUp(self):
        #create file for test
        rasterOrigin = (-10.9472468,-37.0730823)
        pixelWidth = 100
        pixelHeight = 100
        newRasterfn = self.TEST_FILE
        array = np.array([[ 0, 0, 0, 0, 0],
                          [ 255, 255, 255,255, 0],
                          [ 0, 255, 255, 255, 0],
                          [ 255, 255, 255, 255, 0],
                          [ 0, 0, 0, 0, 0]])
        self.array2raster(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array)
        self.rrgb = raster.Raster(self.TEST_FILE, ".")

    def tearDown(self):
        os.remove(self.TEST_FILE)
    

    def test_generate_medians(self):
        self.rrgb._generate_medians()
        assert self.rrgb.B_median > 0
        assert self.rrgb.G_median > 0
        assert self.rrgb.R_median > 0


    # def test_generate_luminance(self):
    #    self.rrgb._generate_luminance()
    #    assert self.rrgb.luminance > 0

    def test_read_img(self):
        """ reimplement this """    
        self.rrgb._generate_bands_arrays()
        assert len(self.rrgb.B) > 0
    
