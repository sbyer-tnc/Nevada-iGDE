#-------------------------------------------------------------------------------
# Name:        NV iGDE Story Map Database - Photo Points
# Purpose:    Create a point layer store photo information for the NV iGDE story map database
#
# Author:      sarah.byer
#
# Created:     May 2019
# Copyright:   (c) sarah.byer 2019
#-------------------------------------------------------------------------------

# Import ArcGIS modules and check out spatial analyst extension
import arcpy, os
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("spatial")

# Path to temporary geodatabase
path =  r"K:\GIS3\Projects\GDE\Geospatial\Geodatabase_Layers\NV_GDE_Template_Temp.gdb"

# Environment settings
env.workspace = path
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference(26911) # Spatial reference NAD 1983 UTM Zone 11N. The code is '26911'

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

# Create photo point feature class
arcpy.CreateFeatureclass_management(out_path = path, out_name = "PhotoPoints", geometry_type = "POINT", spatial_reference = env.outputCoordinateSystem)
arcpy.AddFields_management('PhotoPoints', [['LAYER', 'TEXT', 'Layer', 25],
                                           ['GDE_TYPE', 'TEXT', 'GDE Type', 100],
                                           ['CAPTION', 'TEXT', 'Caption', 255],
                                           ['FLICKR', 'TEXT', 'Flickr Link', 255],
                                           ['JPEG', 'TEXT', 'JPEG Link', 255]])

# Manually add and attribute photo points
# Link to Flickr, JPEG, caption, and give credit    

# Add finished photo points layer to Story Map gdb
photo_points = path + "\\PhotoPoints"
env.workspace = r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_Story_061719.gdb"
arcpy.CopyFeatures_management(photo_points, r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_Story_061719.gdb\NV_Photos")

# END