#-------------------------------------------------------------------------------
# Name:        NV iGDE Database - Lakes and Playas
# Purpose:     Use the NHD to create the Lakes_Playas layer for the NV iGDE database
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

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Load NHD Waterbody Data and filter by FCode

waterbody = r"K:\GIS3\States\NV\NHD\NHD_H_Nevada_State_GDB.gdb\NHDWaterbody"

# Create list of FCodes that will be included in the final layer
# https://nhd.usgs.gov/userguide.html
fcodes = [36100, 39004, 39009, 39011] # Reservoirs/human-altered bodies included with code 39009
# Not including 39010 (perennial, stage = normal pool); only grabs 4 features, none of which look like perennial ponds/pools on imagery.

# Create a copy of the waterbody dataset and filter Fcodes
waterbody_copy = arcpy.CopyFeatures_management(waterbody, "nhd_waterbody_temp")
with arcpy.da.UpdateCursor(waterbody_copy, ['FCode']) as cursor:
    for row in cursor:
        if row[0] not in fcodes:
            print("Deleting features with code {}...".format(row[0]))
            cursor.deleteRow()
del cursor

all_bodies = waterbody_copy
arcpy.GetCount_management(all_bodies)

#-------------------------------------------------------------------------------
# Restrict to extent of NV

# Clip to Nevada
nv = r"K:\GIS3\States\NV\Nevada_83.shp"
body_nv = arcpy.Clip_analysis(all_bodies, nv, "nhd_waterbody_gde_nv")
arcpy.GetCount_management(body_nv)


# Calculate area in acres
arcpy.AddField_management(body_nv, "AREA_ACRES", "DOUBLE")
arcpy.CalculateGeometryAttributes_management(body_nv, [["AREA_ACRES", "AREA"]], "", "ACRES", env.outputCoordinateSystem)

#-------------------------------------------------------------------------------

# Visually compare the waterbodies with NWI coverages and Ken's data when available
# Use these to validate the locations/geometry of the lakes/playas

#-------------------------------------------------------------------------------
# Add to the GDE Template feature class for Lakes/Playas

# Load template feature class
gde_lake_playa = r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_050919.gdb\Lakes_Playas"

# Load lookup table for waterbody types, codes, descriptions
waterbody_lut_file = r"K:\GIS3\Projects\GDE\Tables\NHD_Waterbody_lut.csv"
waterbody_lut = arcpy.TableToTable_conversion(waterbody_lut_file, env.workspace, "nhd_waterbody_lut")

# Populate Type and Description fields using lookup table
arcpy.JoinField_management(body_nv, "FCode", waterbody_lut, "FCode", ["Type", "Description"])
[f.name for f in arcpy.ListFields(body_nv)]

# Define fields to map NHD data to GDE Feature Class
def mapFields(inlayer, infield, mapfield_name, mapfield_alias, mapfield_type): # mapFields function
    fldMap = arcpy.FieldMap()
    fldMap.addInputField(inlayer, infield)
    mapOut = fldMap.outputField
    mapOut.name, mapOut.alias, mapOut.type = mapfield_name, mapfield_alias, mapfield_type
    fldMap.outputField = mapOut
    return fldMap
fcode_map = mapFields(body_nv, "FCode", "BODY_CODE", "Waterbody Code", "LONG")
ftype_map = mapFields(body_nv, "Type", "BODY_TYPE", "Waterbody Type", "TEXT")
desc_map = mapFields(body_nv, "Description", "BODY_DESC", "Waterbody Description", "TEXT")
name_map = mapFields(body_nv, "GNIS_Name", "BODY_NAME", "Waterbody Name", "TEXT")
perm_id_map = mapFields(body_nv, "Permanent_Identifier", "PERM_ID", "Permanent Identifier", "TEXT")
acre_map = mapFields(body_nv, "AREA_ACRES", "AREA_ACRES", "Area (acres)", "DOUBLE")
fldMap_list = [fcode_map, ftype_map, desc_map, name_map, perm_id_map, acre_map]
allFldMappings = arcpy.FieldMappings()
for fm in fldMap_list:
    allFldMappings.addFieldMap(fm)

# Append NHD features to template feature class with field mappings
waterbody_gde = arcpy.Append_management(body_nv, gde_lake_playa, "NO_TEST", allFldMappings)

# Populate Source Codes - all codes = "nhdw"
# National Hydrography Dataset Waterbodies = "nhdw"
with arcpy.da.UpdateCursor(waterbody_gde, ['SOURCE_CODE']) as cursor:
    for row in cursor:
        row[0] = "nhdw"
        cursor.updateRow(row)
del cursor

# END