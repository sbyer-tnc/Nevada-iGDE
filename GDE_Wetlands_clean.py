#-------------------------------------------------------------------------------
# Name:        NV iGDE Database - Wetlands
# Purpose:     Process the EPA Wetland data product to create the NV iGDE Wetlands layer
#
# Author:      sarah.byer
#
# Created:     January 2019
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

# Read in Ken's EPA Nevada Wetland dataset
epa_wetlands = r"K:\GIS3\Projects\GDE\Geospatial\Geodatabase_Layers\GDE_Wetlands\NVwetV1d.gdb\NVwetV1d.gdb\NVwetV1d"

# """NOTE wetland features contributed by TNC: #tnc_wetlands = r"K:\GIS3\Projects\GDE\Geospatial\Geodatabase_Layers\GDE_Wetlands\TNC_Wetland_Phre_050919.shp""""

#-------------------------------------------------------------------------------
# Exclude non-wetland features from the Wetland data

# Make a copy of the original wetland feature class
wet_copy = arcpy.Copy_management(epa_wetlands, "wetlands_copy")

# Remove all Lake features from the copy
with arcpy.da.UpdateCursor(wet_copy, ["WETLAND_TYPE"]) as cursor:
    for row in cursor:
        if row[0] == "Lake":
            print("Deleting {} as a non-wetland feature".format(row[0]))
            cursor.deleteRow()
del cursor


# Remove dry playas
with arcpy.da.UpdateCursor(wet_copy, ["WETLAND_SUBTYPE"]) as cursor:
    for row in cursor:
        if row[0] == "dry":
            print("Deleting dry playa as a non-wetland feature")
            cursor.deleteRow()
del cursor


# Add source code field and populate
# Desert Research Institute Wetlands = "driw"
arcpy.AddField_management(wet_copy, "SOURCECODE", "TEXT")
with arcpy.da.UpdateCursor(wet_copy, ["SOURCECODE"]) as cursor:
    for row in cursor:
        row[0] = "driw"
        cursor.updateRow(row)
del cursor

#-------------------------------------------------------------------------------
# Add wetland features to GDE database

gde_wetlands = r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_050919.gdb\Wetlands"

# Map to GDE Wetland layer and poy polygon features there:
def mapFields(inlayer, infield, mapfield_name, mapfield_alias, mapfield_type): # mapFields function
    fldMap = arcpy.FieldMap()
    fldMap.addInputField(inlayer, infield)
    mapOut = fldMap.outputField
    mapOut.name, mapOut.alias, mapOut.type = mapfield_name, mapfield_alias, mapfield_type
    fldMap.outputField = mapOut
    return fldMap

# Field mapping for Wetlands layer
wet_type_map = mapFields(wet_copy, "WETLAND_TYPE", "WET_TYPE", "Wetland Type", "TEXT")
wet_subtype_map = mapFields(wet_copy, "WETLAND_SUBTYPE", "WET_SUBTYPE", "Wetland Subtype", "TEXT")
source_map = mapFields(wet_copy, "SOURCECODE", "SOURCE_CODE", "Source Code", "TEXT")
fldMap_list = [wet_type_map, wet_subtype_map, source_map]
wetFldMappings = arcpy.FieldMappings()
for fm in fldMap_list:
    wetFldMappings.addFieldMap(fm)

# Append to GDE database Wetland layer
arcpy.Append_management(wet_copy, gde_wetlands, "NO_TEST", wetFldMappings)

# END