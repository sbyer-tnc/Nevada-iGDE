#-------------------------------------------------------------------------------
# Name:        Create NV GDE Geodatabase Template
# Purpose:     Create the layers and fields that will be included in the NV GDE database. No data will be added to the template in this script.
#
# Author:      sarah.byer
#              Spatial/GIS Analyst
#              The Nature Conservancy, Nevada Chapter
#
# Created:     24/09/2018
# Copyright:   (c) sarah.byer 2018

#-------------------------------------------------------------------------------

# Load packages
import arcpy, os
from arcpy import env

# Environment Settings
path = r"K:\GIS3\Projects\GDE\Geospatial"
#path = r"D:\NV_GDE\Data"
os.chdir(path)
env.overwriteOutput = True # Choose to overwrite files

#-------------------------------------------------------------------------------
# Create empty geodatabase as the NV GDE template
#arcpy.CreateFileGDB_management(path, "NV_GDE_Template")
#arcpy.CreateFileGDB_management(path, "NV_GDE_Template_Temp")
arcpy.CreateFileGDB_management(path, "NV_GDE_011619")
#gdb = path + r"\NV_GDE_Template.gdb" # 'gdb' is the object for WHAP_Template.gdb
#gdb = r"K:\GIS3\Projects\GDE\Geospatial\NV_GDE_123118.gdb"
gdb = r"K:\GIS3\Projects\GDE\Geospatial\NV_GDE_011619.gdb"
env.workspace = gdb
arcpy.ListFeatureClasses() # Will return a blank list if database hasn't been created yet
arcpy.ListTables()

#-------------------------------------------------------------------------------
# Create layers/tables in the empty geodatabase
NAD83UTM11N = arcpy.SpatialReference(26911) # Spatial reference NAD 1983 UTM Zone 11N. The code is '26911'
NAD83UTM11N.exportToString() # Print detailed spatial reference information

# Vegetation/Phreatophyte
#arcpy.CreateFeatureclass_management(out_path = gdb, out_name = "Vegetation", geometry_type = "POLYGON", spatial_reference = NAD83UTM11N)
arcpy.CreateFeatureclass_management(out_path = gdb, out_name = "Phreatophytes", geometry_type = "POLYGON", spatial_reference = NAD83UTM11N)
arcpy.AddFields_management('Phreatophytes', [['SOURCE_CODE', 'TEXT', 'Source Code', 10],
                                           ['PHR_TYPE', 'TEXT', 'Phreatophyte Type', 55],
                                           ['PHR_CODE', 'TEXT', 'Phreatophyte Code', 20],
                                           ['PHR_GROUP', 'TEXT', 'Phreatophyte Group', 20],
#                                           ['GDE_STAT', 'SHORT', 'GDE Status'],
                                           ['COMMENTS', 'TEXT', 'Comments', 200]])
[f.name for f in arcpy.ListFields(gdb + "\\Phreatophytes")] # List all of the field names in the Phreatophytes layer

# Springs
arcpy.CreateFeatureclass_management(out_path = gdb, out_name = "Springs", geometry_type = "POINT", spatial_reference = NAD83UTM11N)
arcpy.AddFields_management('Springs', [['SOURCE_CODE', 'TEXT', 'Source Code', 10],
                                           ['SPRING_ID', 'LONG', 'Spring ID'],
                                           ['SPRING_NAME', 'TEXT', 'Spring Name', 255],
                                           ['SPRING_TYPE1', 'TEXT', 'Spring Type 1', 20],
                                           ['SPRING_TYPE2', 'TEXT', 'Spring Type 2', 20],
#                                           ['COUNTY', 'TEXT', 'County', 30],
#                                           ['SPRING_MANAGER', 'TEXT', 'Spring Manager', 50],
                                           ['IMAGE_LINK', 'TEXT', 'Image Hyperlink', 255],
                                           ['SKETCH_LINK', 'TEXT', 'Sketch Hyperlink', 255],
                                           ['LATITUDE', 'DOUBLE', 'Latitude'],
                                           ['LONGITUDE', 'DOUBLE', 'Longitude'],
                                           ['ELEVATION', 'DOUBLE', 'Elevation (m)'],
                                           ['INV_STAT', 'TEXT', 'Inventory Status', 20],
                                           ['SURV_COUNT', 'SHORT', 'Survey Count'],
                                           ['FLOW_MEAN', 'DOUBLE', 'Flow Mean ()'], # Get units for values
                                           ['PH_MEAN', 'DOUBLE', 'pH Mean ()'], # Get units for values
                                           ['WATER_TEMP_MEAN', 'DOUBLE', 'Water Temperature Mean ()'], # Get units for values
                                           ['SPEC_COND_MEAN', 'DOUBLE', 'Spec Cond Mean ()'], # Get units for values AND a definition of this field...
                                           ['ALKALINITY_MEAN', 'DOUBLE', 'Alkalinity Mean ()'], # Get units for values
                                           ['AREA', 'DOUBLE', 'Area (m2)'],
                                           ['VERT_COUNT', 'LONG', 'Vertebrate Species Count'],
                                           ['INVERT_COUNT', 'LONG', 'Invertebrate Species Count'],
                                           ['FLORA_COUNT', 'LONG', 'Plant Species Count'],
                                           ['COMMENTS', 'TEXT', 'Comments', 200]])

# Wetlands
arcpy.CreateFeatureclass_management(out_path = gdb, out_name = "Wetlands", geometry_type = "POLYGON", spatial_reference = NAD83UTM11N)
arcpy.AddFields_management('Wetlands', [['SOURCE_CODE', 'TEXT', 'Source Code', 10],
                                           ['WETLAND_TYPE', 'TEXT', 'Wetland Type', 50],
                                           ['WETLAND_CODE', 'TEXT', 'Wetland Code', 20],
#                                           ['SPP_SITE', 'TEXT', 'Species Site ID', 50],
                                           ['ELEV_MEAN', 'DOUBLE', 'Mean Elevation (m)'],
                                           ['SLOPE_MEAN', 'DOUBLE', 'Mean Slope (%)'],
                                           ['PRECIP_MEAN', 'DOUBLE', 'Mean Precipitation (mm)'],
                                           ['TEMP_MEAN', 'DOUBLE', 'Mean Monthly Temperature (C)'],
                                           ['WETLAND_SCORE', 'DOUBLE', 'Wetland Score'],
                                           ['COMMENTS', 'TEXT', 'Comments', 200]],)

# Lakes_Playas
arcpy.CreateFeatureclass_management(out_path = gdb, out_name = "Lakes_Playas", geometry_type = "POLYGON", spatial_reference = NAD83UTM11N)
arcpy.AddFields_management('Lakes_Playas', [['PERM_ID', 'TEXT', 'Permanent Identifier', 255],
                                           ['BODY_NAME', 'TEXT', 'Waterbody Name', 200],
                                           ['BODY_TYPE', 'TEXT', 'Waterbody Type', 50],
                                           ['BODY_CODE', 'LONG', 'Waterbody Code'], 
                                           ['BODY_DESC', 'TEXT', 'Waterbody Description', 200],
                                           ['AREA_ACRES', 'DOUBLE', 'Area (acres)'],
                                           ['SOURCE_CODE', 'TEXT', 'Source Code', 10],
                                           ['COMMENTS', 'TEXT', 'Comments', 200]])
# Ask Laurel if body code is necessary, since we're including the permanent ID and will likely include this info in the methods report

# Rivers
arcpy.CreateFeatureclass_management(out_path = gdb, out_name = "Rivers", geometry_type = "POLYLINE", spatial_reference = NAD83UTM11N)
arcpy.AddFields_management('Rivers', [['PERM_ID', 'TEXT', 'Permanent Identifier', 255],
                                       ['RIVER_NAME', 'TEXT', 'River Name', 200],
                                       ['RIVER_CODE', 'LONG', 'River Code'],
                                       ['RIVER_TYPE', 'TEXT', 'River Type', 100],
                                       ['RIVER_DESC', 'TEXT', 'River Description', 100],
                                       ['LENGTH_M', 'DOUBLE', 'Length (meters)'],
                                       ['SOURCE_CODE', 'TEXT', 'Source Code', 10],
                                       ['COMMENTS', 'TEXT', 'Comments', 200]])
# Ask Laurel if river code is necessary, since we're including the permanent ID and will likely include this info in the methods report

# Species
# Create species table
arcpy.CreateTable_management(out_path = gdb, out_name = 'Species_tbl')
arcpy.AddFields_management('Species_tbl', [['HEX_ID', 'LONG', 'Hexagon ID'],   
#                                       ['SPP_SITE', 'TEXT', 'Species Site ID', 50],
                                       ['SCI_NAME', 'TEXT', 'Scientific Name', 80],
                                       ['COM_NAME', 'TEXT', 'Common Name', 80],
#                                       ['ALT_SCI_NAME', 'TEXT', 'Alternate Scientific Name', 80],
                                       ['ORDER', 'TEXT', 'Order', 30],
                                       ['FAMILY', 'TEXT', 'Family', 30],
                                       ['MAJOR_GROUP', 'TEXT', 'Major Taxanomic Group', 20],
                                       ['MINOR_GROUP', 'TEXT', 'Minor Taxanomic Group', 20],
                                       ['NV_STATUS', 'TEXT', 'Nevada Conservation Status', 20],
                                       ['G_STATUS', 'TEXT', 'Global Conservation Status', 20],
                                       ['ESA_STATUS', 'TEXT', 'ESA Conservation Status', 20],
                                       ['ENDEMISM', 'TEXT', 'Endemism', 20],
                                       ['SOURCE_CODE', 'TEXT', 'Source Code', 10],
                                       ['COMMENTS', 'TEXT', 'Comments', 200]])
# Create species summary polygons
arcpy.CreateFeatureclass_management(out_path = gdb, out_name = 'Species', geometry_type = "POLYGON", spatial_reference = NAD83UTM11N)
arcpy.AddFields_management('Species', [['HEX_ID', 'LONG', 'Hexagon ID'],
                                       ['SPP_COUNT', 'LONG', 'Species Count'],
                                       ['SOURCE_CODE', 'TEXT', 'Source Code', 10],
                                       ['COMMENTS', 'TEXT', 'Comments', 200]])
# Create relationship between species polygons and table
# RUN IN THE SPECIES SCRIPT (GDE_Species.py)
#arcpy.CreateRelationshipClass_management('Species', 'Species_tbl', 'Species_tbl_relate', 'SIMPLE', 'Species_tbl', 'Species_grid', 'NONE', 'ONE_TO_MANY', 'NONE', 'GRID_ID', 'GRID_ID')

# Boundaries
#arcpy.CreateFeatureclass_management(out_path = gdb, out_name = "Boundaries", geometry_type = "POLYGON", spatial_reference = NAD83UTM11N)
#arcpy.AddFields_management('Boundaries', [['SOURCE_CODE', 'TEXT', 'Source Code', 10],
#                                          ['OWNER_NAME', 'TEXT', 'Owner Name', 100],
#                                          ['OWNER_TYPE', 'TEXT', 'Owner Type', 30],
#                                          ['MANAGER_NAME', 'TEXT', 'Manger Name', 100],
#                                          ['MANAGER_TYPE', 'TEXT', 'Manager Type', 30],
#                                          ['MANAGER_LOCAL', 'TEXT', 'Local Manager Name', 30],
#                                          ['HYD_BASIN_ID', 'LONG', 'Hydrologic Basin ID'],
#                                          ['HYD_BASIN_NAME', 'TEXT', 'Hydrologic Basin Name', 30],
#                                          ['COMMENTS', 'TEXT', 'Comments', 200]])

# Sources
arcpy.CreateTable_management(out_path = gdb, out_name = 'Sources')
arcpy.AddFields_management('Sources', [['SOURCE_CODE', 'TEXT', 'Source Code', 10],
                                       ['SOURCE_DATE', 'DATE', 'Source Date'],
                                       ['SOURCE_NAME', 'TEXT', 'Source Name', 255],
                                       ['SOURCE_GROUP', 'TEXT', 'Source Group', 40],
                                       ['SOURCE_LINK', 'TEXT', 'Source Link', 255],
                                       ['SOURCE_CITE', 'TEXT', 'Source Citation', 255],
                                       ['MAP_METHOD', 'TEXT', 'Mapping Method', 255],
                                       ['MAP_UNIT', 'DOUBLE', 'Minimum Mapping Unit'],
                                       ['COMMENTS', 'TEXT', 'Comments', 255]])
# Create relationship between sources table and all other feature classes/tables in the gdb
### WRITE HERE

#-------------------------------------------------------------------------------
# Populate source table
gde_source = gdb + "\\Sources"
[f.name for f in arcpy.ListFields(gde_source)]
source_tbl = r"K:\GIS3\Projects\GDE\Tables\gde_source_tbl_123118.csv"
[f.name for f in arcpy.ListFields(source_tbl)]

# Create custom function for field mapping
def mapFields(inlayer, infield, mapfield_name, mapfield_alias, mapfield_type): # mapFields function
    fldMap = arcpy.FieldMap()
    fldMap.addInputField(inlayer, infield)
    mapOut = fldMap.outputField
    mapOut.name, mapOut.alias, mapOut.type = mapfield_name, mapfield_alias, mapfield_type
    fldMap.outputField = mapOut
    return fldMap

# Field mapping for Springs (from fishnet_nnhp_spp_names to GDE Species_tbl)
source_map = mapFields(source_tbl, "SOURCE_CODE", "SOURCE_CODE", "Source Code", "TEXT")
date_map = mapFields(source_tbl, "SOURCE_DATE", "SOURCE_DATE", "Source Date", "DATE")
name_map = mapFields(source_tbl, "SOURCE_NAME", "SOURCE_NAME", "Source Name", "TEXT")
group_map = mapFields(source_tbl, "Layer", "SOURCE_GROUP", "Source Group", "TEXT")
#link_map = mapFields(source_tbl, "SOURCE_LINK", "SOURCE_LINK", "Source Link", "TEXT")
cite_map = mapFields(source_tbl, "SOURCE_CITE", "SOURCE_CITE", "Source Citation", "TEXT")
method_map = mapFields(source_tbl, "MAP_METHOD", "MAP_METHOD", "Mapping Method", "TEXT")
unit_map = mapFields(source_tbl, "MAP_UNIT", "MAP_UNIT", "Minimum Mapping Unit", "DOUBLE")
comment_map = mapFields(source_tbl, "COMMENTS", "COMMENTS", "Comments", "TEXT")

maplist = [source_map, date_map, name_map, group_map, cite_map, method_map, unit_map, comment_map]
sourceFldMappings = arcpy.FieldMappings()
for fm in maplist:
    sourceFldMappings.addFieldMap(fm)
    
# Append to GDE database Sources Table
arcpy.Append_management([source_tbl], gde_source, "NO_TEST", sourceFldMappings)    

### Need to make sure that SOURCE_DATE field turns out properly. Later...

#-------------------------------------------------------------------------------
# Copy geodatabase from external hard drive to K-drive

gdb = r"D:\NV_GDE\Data\NV_GDE_Template.gdb"
arcpy.Copy_management(gdb, r"K:\GIS3\Projects\GDE\Geospatial\NV_GDE_123118.gdb")








