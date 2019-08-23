#-------------------------------------------------------------------------------
# Name:        Create NV Indicators of Groundwater Dependent Ecosystem (iGDE) Geodatabase Template
# Purpose:     Create the full and story map geodatabases with layers and fields that will be included in the Nevada iGDE database. No data will be added to the template in this script except for the Source data table in the full database.
# Modules: arcpy; os
#
# Author:      Sarah Byer (sarah.byer@tnc.org)
#              Spatial/GIS Analyst
#              The Nature Conservancy, Nevada Chapter
#
# Last edited:  08 July 2019
# Copyright:   (c) sarah.byer/TNC 2019

#-------------------------------------------------------------------------------
# Load modules and packages
import arcpy, os
from arcpy import env

# Set Environment Settings
path = r"K:\GIS3\Projects\GDE\Geospatial"
os.chdir(path)
env.overwriteOutput = True

#-------------------------------------------------------------------------------
# Create empty geodatabase as the NV GDE template
# Naming scheme used: "NV_GDE_MMDDYY"
gdb_name = "NV_iGDE_050919"
arcpy.CreateFileGDB_management(path, gdb_name) # Only use this once
gdb = path + "\\" + gdb_name + ".gdb" # path to the geodatabase

# Change environment setting to the new geodatabase
env.workspace = gdb

# Examine geodatabase for feature classes/tables
arcpy.ListFeatureClasses() # Will return a blank list if database has just been created
arcpy.ListTables() # Will return a blank list if database has just been created

#-------------------------------------------------------------------------------
# Create layers/tables in the empty geodatabase

# Define spatial reference for the geodatabase
# http://pro.arcgis.com/en/pro-app/arcpy/classes/pdf/projected_coordinate_systems.pdf
NAD83UTM11N = arcpy.SpatialReference(26911) # Spatial reference NAD 1983 UTM Zone 11N. The WKID is '26911'
NAD83UTM11N.exportToString() # Print detailed spatial reference information


# Phreatophyte - polygon feature class
arcpy.CreateFeatureclass_management(out_path = gdb, out_name = "Phreatophytes", geometry_type = "POLYGON", spatial_reference = NAD83UTM11N)
arcpy.AddFields_management('Phreatophytes', [['SOURCE_CODE', 'TEXT', 'Source Code', 10],
                                           ['PHR_TYPE', 'TEXT', 'Phreatophyte Type', 55],
                                           ['PHR_GROUP', 'TEXT', 'Phreatophyte Group', 20],
                                           ['COMMENTS', 'TEXT', 'Comments', 200]])
[f.name for f in arcpy.ListFields(gdb + "\\Phreatophytes")] # List all of the field names in the Phreatophytes layer


# Springs - point feature class
arcpy.CreateFeatureclass_management(out_path = gdb, out_name = "Springs", geometry_type = "POINT", spatial_reference = NAD83UTM11N)
arcpy.AddFields_management('Springs', [['SOURCE_CODE', 'TEXT', 'Source Code', 10],
                                           ['SPRING_ID', 'LONG', 'Spring ID'],
                                           ['SPRING_NAME', 'TEXT', 'Spring Name', 255],
                                           ['SPRING_TYPE1', 'TEXT', 'Spring Type 1', 20],
                                           ['SPRING_TYPE2', 'TEXT', 'Spring Type 2', 20],
                                           ['IMAGE_LINK', 'TEXT', 'Image Hyperlink', 255],
                                           ['SKETCH_LINK', 'TEXT', 'Sketch Hyperlink', 255],
                                           ['LATITUDE', 'DOUBLE', 'Latitude'],
                                           ['LONGITUDE', 'DOUBLE', 'Longitude'],
                                           ['ELEVATION', 'DOUBLE', 'Elevation (m)'],
                                           ['INV_STAT', 'TEXT', 'Inventory Status', 20],
                                           ['SURV_COUNT', 'SHORT', 'Survey Count'],
                                           ['FLOW_MEAN', 'DOUBLE', 'Flow Mean (L/s)'],
                                           ['PH_MEAN', 'DOUBLE', 'pH Mean'],
                                           ['WATER_TEMP_MEAN', 'DOUBLE', 'Water Temperature Mean (C)'],
                                           ['SPEC_COND_MEAN', 'DOUBLE', 'Specific Conductance Mean (uS/cm)'],
                                           ['ALKALINITY_MEAN', 'DOUBLE', 'Alkalinity Mean (mg/L)'],
                                           ['SPRING_AREA', 'DOUBLE', 'Spring Area (m2)'],
                                           ['VERT_COUNT', 'LONG', 'Vertebrate Species Count'],
                                           ['INVERT_COUNT', 'LONG', 'Invertebrate Species Count'],
                                           ['FLORA_COUNT', 'LONG', 'Plant Species Count'],
                                           ['COMMENTS', 'TEXT', 'Comments', 200]])
[f.name for f in arcpy.ListFields(gdb + "\\Springs")] # List all of the field names in the Springs layer


# Wetlands - polygon feature class
arcpy.CreateFeatureclass_management(out_path = gdb, out_name = "Wetlands", geometry_type = "POLYGON", spatial_reference = NAD83UTM11N)
arcpy.AddFields_management('Wetlands', [['WET_TYPE', 'TEXT', 'Wetland Type', 30],
                                           ['WET_SUBTYPE', 'TEXT', 'Wetland Subtype', 30],
                                           ['SOURCE_CODE', 'TEXT', 'Source Code', 10],
                                           ['COMMENTS', 'TEXT', 'Comments', 200]],)
[f.name for f in arcpy.ListFields(gdb + "\\Wetlands")] # List all of the field names in the Wetlands layer


# Lakes & Playas - polygon feature class
arcpy.CreateFeatureclass_management(out_path = gdb, out_name = "Lakes_Playas", geometry_type = "POLYGON", spatial_reference = NAD83UTM11N)
arcpy.AddFields_management('Lakes_Playas', [['PERM_ID', 'TEXT', 'Permanent Identifier', 255],
                                           ['BODY_NAME', 'TEXT', 'Waterbody Name', 200],
                                           ['BODY_TYPE', 'TEXT', 'Waterbody Type', 50],
                                           ['BODY_CODE', 'LONG', 'Waterbody Code'], 
                                           ['BODY_DESC', 'TEXT', 'Waterbody Description', 200],
                                           ['AREA_ACRES', 'DOUBLE', 'Area (acres)'],
                                           ['SOURCE_CODE', 'TEXT', 'Source Code', 10],
                                           ['COMMENTS', 'TEXT', 'Comments', 200]])
[f.name for f in arcpy.ListFields(gdb + "\\Lakes_Playas")] # List all of the field names in the Lakes_Playas layer


# Rivers/Streams - polyline feature class
arcpy.CreateFeatureclass_management(out_path = gdb, out_name = "Rivers_Streams", geometry_type = "POLYLINE", spatial_reference = NAD83UTM11N)
arcpy.AddFields_management('Rivers_Streams', [['PERM_ID', 'TEXT', 'Permanent Identifier', 255],
                                       ['RIVER_NAME', 'TEXT', 'River Name', 200],
                                       ['RIVER_CODE', 'LONG', 'River Code'],
                                       ['RIVER_TYPE', 'TEXT', 'River Type', 100],
                                       ['LENGTH_MI', 'DOUBLE', 'Length (miles)'],
                                       ['SOURCE_CODE', 'TEXT', 'Source Code', 10],
                                       ['COMMENTS', 'TEXT', 'Comments', 200]])
[f.name for f in arcpy.ListFields(gdb + "\\Rivers_Streams")] # List all of the field names in the Rivers layer


# Species
# Create species table
arcpy.CreateTable_management(out_path = gdb, out_name = 'Species_tbl')
arcpy.AddFields_management('Species_tbl', [['SCI_NAME', 'TEXT', 'Scientific Name', 80],
                                       ['COM_NAME', 'TEXT', 'Common Name', 80],
                                       ['MAJOR_GROUP', 'TEXT', 'Major Taxonomic Group', 20],
                                       ['MINOR_GROUP', 'TEXT', 'Minor Taxonomic Group', 20],
                                       ['NV_RANK', 'TEXT', 'NV Conservation Status Rank', 20],
                                       ['G_RANK', 'TEXT', 'Global Conservation Status Rank', 20],
                                       ['NV_STATUS', 'TEXT', 'NV Protection Status', 20],
                                       ['ESA_STATUS', 'TEXT', 'ESA Conservation Status', 20],
                                       ['BLM_STATUS', 'TEXT', 'BLM Conservation Status', 20],
                                       ['USFS_STATUS', 'TEXT', 'USFS Conservation Status', 20],
                                       ['NNPS_STATUS', 'TEXT', 'NNPS Conservation Status', 20],
                                       ['WAP2012', 'TEXT', 'WAP 2012 Species of Conservation Priority', 20],
                                       ['ENDEMISM', 'TEXT', 'Endemism', 20],
                                       ['NNHP_LIST', 'TEXT', 'NNHP List', 20],
                                       ['SOURCE_CODE', 'TEXT', 'Source Code', 10],
                                       ['COMMENTS', 'TEXT', 'Comments', 200]])
[f.name for f in arcpy.ListFields(gdb + "\\Species_tbl")] # List all of the field names in the Species table

# Create species polygon layer
arcpy.CreateFeatureclass_management(out_path = gdb, out_name = 'Species', geometry_type = "POLYGON", spatial_reference = NAD83UTM11N)
arcpy.AddFields_management('Species', [['HEX_ID', 'LONG', 'Hexagon ID'],   
                                       ['COUNT_NNHP', 'LONG', 'NNHP Species Count'],
                                       ['COUNT_EN', 'LONG', 'Endemic Species Count'],
                                       ['SOURCE_CODE', 'TEXT', 'Source Code', 10],
                                       ['COMMENTS', 'TEXT', 'Comments', 200]])
[f.name for f in arcpy.ListFields(gdb + "\\Species")] # List all of the field names in the Species layer


# Source table
arcpy.CreateTable_management(out_path = gdb, out_name = 'Source_tbl')
arcpy.AddFields_management('Source_tbl', [['SOURCE_CODE', 'TEXT', 'Source Code', 10],
                                       ['SOURCE_NAME', 'TEXT', 'Source Name', 255],
                                       ['SOURCE_BODY', 'TEXT', 'Source Originating Body', 255],
                                       ['LAYER', 'TEXT', 'Layers Using Source', 80],
                                       ['SOURCE_LINK', 'TEXT', 'Source Link', 255],
                                       ['SOURCE_CITE', 'TEXT', 'Source Citation', 255],
                                       ['MAP_METHOD', 'TEXT', 'Mapping Method', 255],
                                       ['MAP_UNIT', 'DOUBLE', 'Minimum Mapping Unit'],
                                       ['COMMENTS', 'TEXT', 'Comments', 255],
                                       ['SOURCE_YEAR', 'LONG', 'SOURCE_YEAR']])
[f.name for f in arcpy.ListFields(gdb + "\\Source_tbl")] # List all of the field names in the Source_tbl layer

#-------------------------------------------------------------------------------
# Populate source table

# Create variable for the Source Table
gde_source = gdb + "\\Source_tbl"

# Read in the source table
source_tbl = r"K:\GIS3\Projects\GDE\Tables\gde_source_tbl_050919.csv" # path to source table

# Field mapping to populate Source_tbl template using the above csv
def mapFields(inlayer, infield, mapfield_name, mapfield_alias, mapfield_type): # mapFields function
    fldMap = arcpy.FieldMap()
    fldMap.addInputField(inlayer, infield)
    mapOut = fldMap.outputField
    mapOut.name, mapOut.alias, mapOut.type = mapfield_name, mapfield_alias, mapfield_type
    fldMap.outputField = mapOut
    return fldMap

source_map = mapFields(source_tbl, "SOURCE_CODE", "SOURCE_CODE", "Source Code", "TEXT")
name_map = mapFields(source_tbl, "SOURCE_NAME", "SOURCE_NAME", "Source Name", "TEXT")
body_map = mapFields(source_tbl, "SOURCE_BODY", "SOURCE_BODY", "Source Originating Body", "TEXT")
layer_map = mapFields(source_tbl, "LAYER", "LAYER", "Layers Using Source", "TEXT")
link_map = mapFields(source_tbl, "SOURCE_LINK", "SOURCE_LINK", "Source Link", "TEXT")
cite_map = mapFields(source_tbl, "SOURCE_CITE", "SOURCE_CITE", "Source Citation", "TEXT")
method_map = mapFields(source_tbl, "MAP_METHOD", "MAP_METHOD", "Mapping Method", "TEXT")
unit_map = mapFields(source_tbl, "MAP_UNIT", "MAP_UNIT", "Minimum Mapping Unit", "DOUBLE")
comment_map = mapFields(source_tbl, "COMMENTS", "COMMENTS", "Comments", "TEXT")
year_map = mapFields(source_tbl, "SOURCE_YEAR", "SOURCE_YEAR", "SOURCE_YEAR", "LONG")


# Create the FieldMappings objec
maplist = [source_map, name_map, body_map, layer_map, link_map, cite_map, method_map, unit_map, comment_map, year_map]
sourceFldMappings = arcpy.FieldMappings()
for fm in maplist:
    sourceFldMappings.addFieldMap(fm)
    
# Append the source data to Source_tbl using the FieldMappings object (above)
arcpy.Append_management([source_tbl], gde_source, "NO_TEST", sourceFldMappings)   

# END