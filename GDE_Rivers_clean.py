#-------------------------------------------------------------------------------
# Name:        NV iGDE Database - Rivers and Streams
# Purpose:     Process NHD data to create the Rivers_Streams layer for the NV iGDE database
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

# Load NHD Flowline Data
flowline = r"K:\GIS3\States\NV\NHD\NHD_H_Nevada_State_GDB.gdb\NHDFlowline"

# Create flowline dataset with only perennial streams/rivers
# https://nhd.usgs.gov/userguide.html
flowline_copy = arcpy.CopyFeatures_management(flowline, "nhd_flowline_temp")
with arcpy.da.UpdateCursor(flowline_copy, ['FCode']) as cursor:
    for row in cursor:
        if row[0] != 46006:
            print("Deleting features with code {}...".format(row[0]))
            cursor.deleteRow()
del cursor

#-------------------------------------------------------------------------------
# Create a flowline dataset with major Nevada rivers/streams

# Make a copy of NHDFlowline
flowline_major = arcpy.CopyFeatures_management(flowline, "nhd_flowline_major")

# Allowable FCode list
fcodes = [55800, 46006] # Articifial Path, Stream/River Perennial

# Select features that are not artificial paths or perennial streams/rivers and delete from feature class
with arcpy.da.UpdateCursor(flowline_major, ['FCode']) as cursor:
    for row in cursor:
        if row[0] not in fcodes:
            cursor.deleteRow()
            print("Deleting river section with FCode: {}".format(row[0]))
del cursor

# Major rivers/streams names to include from table
major_tbl = r"K:\GIS3\Projects\GDE\Tables\NV_GDE_Major_RiversStreams.csv"
[f.name for f in arcpy.ListFields(major_tbl)]
river_names = []
with arcpy.da.SearchCursor(major_tbl, ['Name']) as cursor:
    for row in cursor:
        river_names.append(row[0])
del cursor
print(river_names)

# Delete all features that are not named in the major rivers list
with arcpy.da.UpdateCursor(flowline_major, ['GNIS_Name', 'FCode']) as cursor:
    for row in cursor:
        if not any(river in str(row[0]) for river in river_names):
            print("Deleting section: {}".format(row[0]))
            cursor.deleteRow()
del cursor

# Delete artificial path segment of the Quinn River that runs through Black Rock Desert by removing its permanent ID values
permid_select = "Permanent_Identifier NOT BETWEEN '152068036' AND '152068098'"
flowline_ids = arcpy.Select_analysis(flowline_major, "flowline_ids", permid_select)

# Remove 'White River Wash' - not a major river
wr_select = "GNIS_Name <> 'White River Wash'"
flowline_select = arcpy.Select_analysis(flowline_ids, "flowline_select", wr_select)


# Combine all-perennials with major streams/rivers by removing duplicates from all-perennials
# Get list of all permanent ids from major streams/rivers feature class; they will all be unique
major_ids = list()
with arcpy.da.SearchCursor(flowline_select, ['Permanent_Identifier']) as cursor:
    for row in cursor:
        perm_id = row[0]
        major_ids.append(perm_id)
del cursor
len(set(major_ids)) == len(major_ids) # Check all ids are unique, this expression should be True


# Copy the all-perennial feature class
flowline_perennial = arcpy.Copy_management(flowline_copy, "flowline_perennial")

# Count number of features and number of unique perennial IDs - should be equal
count_peren = int(str(arcpy.GetCount_management(flowline_perennial)))
peren_ids = []
with arcpy.da.SearchCursor(flowline_perennial, ['Permanent_Identifier']) as cursor:
    for row in cursor:
        perm_id = row[0]
        peren_ids.append(perm_id)
del cursor
len(set(peren_ids))


# Delete features from all-perennial feature class that are already in the major rivers/streams feature class
dupes = []
with arcpy.da.UpdateCursor(flowline_perennial, ['Permanent_Identifier']) as cursor:
    for row in cursor:
        if row[0] in major_ids:
            dupes.append(row[0])
            print("Deleting duplicate ID {}".format(row[0]))
            cursor.deleteRow()
del cursor
len(dupes)
count_peren == int(str(arcpy.GetCount_management(flowline_perennial))) + len(dupes) # Should be True

# Append all-perennial features to major rivers/streams feature class
rivers = arcpy.Copy_management(flowline_select, "flowline_gdes")
arcpy.Append_management(flowline_perennial, rivers, "NO_TEST")
arcpy.GetCount_management(rivers)

# Clip to Nevada
nv = r"K:\GIS3\States\NV\Nevada_83.shp"
river_nv = arcpy.Clip_analysis(rivers, nv, "flowline_gdes_nv")

# Calculate river length in miles
arcpy.AddField_management(river_nv, "LENGTH_MI", "DOUBLE")
arcpy.CalculateGeometryAttributes_management(river_nv, [["LENGTH_MI", "LENGTH"]], "MILES_US", "", env.outputCoordinateSystem)

# Create & populate a river type attribute using FCode
arcpy.AddField_management(river_nv, "RIVER_TYPE", "TEXT")
with arcpy.da.UpdateCursor(river_nv, ['FCode', 'RIVER_TYPE']) as cursor:
    for row in cursor:
        if row[0] == 46006:
            row[1] = "Perennial Stream/River"
            cursor.updateRow(row)
        else:
            row[1] = "Artificial Path"
            cursor.updateRow(row)
del cursor

#-------------------------------------------------------------------------------
# Add to the GDE Template feature class for Rivers

gde_rivers = r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_050919.gdb\Rivers_Streams"

# Define map fields to append river features to GDE River Template
def mapFields(inlayer, infield, mapfield_name, mapfield_alias, mapfield_type): # mapFields function
    fldMap = arcpy.FieldMap()
    fldMap.addInputField(inlayer, infield)
    mapOut = fldMap.outputField
    mapOut.name, mapOut.alias, mapOut.type = mapfield_name, mapfield_alias, mapfield_type
    fldMap.outputField = mapOut
    return fldMap

# Append NHD features to template feature class with field mappings
name_map = mapFields(river_nv, "GNIS_Name", "RIVER_NAME", "River Name", "TEXT")
type_map = mapFields(river_nv, "RIVER_TYPE", "RIVER_TYPE", "River Type", "TEXT")
code_map = mapFields(river_nv, "FCode", "RIVER_CODE", "River Code", "LONG")
length_map = mapFields(river_nv, "LENGTH_MI", "LENGTH_MI", "Length (miles)", "DOUBLE")
perm_id_map = mapFields(river_nv, "Permanent_Identifier", "PERM_ID", "Permanent Identifier", "TEXT")
fldMap_list = [name_map, type_map, code_map, length_map, perm_id_map]
allFldMappings = arcpy.FieldMappings()
for fm in fldMap_list:
    allFldMappings.addFieldMap(fm)
river_gde = arcpy.Append_management(river_nv, gde_rivers, "NO_TEST", allFldMappings)
    
# Populate source code field
# National Hydrography Dataset Flowline = "nhdf"
with arcpy.da.UpdateCursor(river_gde, ['SOURCE_CODE']) as cursor:
    for row in cursor:
        row[0] = "nhdf"
        cursor.updateRow(row)
del cursor

# END