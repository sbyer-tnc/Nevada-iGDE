#-------------------------------------------------------------------------------
# Name:        NV iGDE Database - Species
# Purpose:     Use NNHP species data to create a Species layer and table for the NV iGDE database
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
# Create copy of the hexagons from NV CHAT
# Used to summarizes spatial species data
area_unit = r"K:\GIS3\Projects\GDE\Geospatial\Geodatabase_Layers\GDE_Boundaries\nv_chat_polygons.shp"
gde_unit = arcpy.CopyFeatures_management(area_unit, "hexagon_units_temp")

#-------------------------------------------------------------------------------
# Format species data from NNHP

species_point = r"K:\GIS3\States\NV\NNHP_DONOTSHARE\TNC_GDE_2019\TNC_GDE_Project_point.shp"
species_line = r"K:\GIS3\States\NV\NNHP_DONOTSHARE\TNC_GDE_2019\TNC_GDE_Project_line.shp"
species_poly = r"K:\GIS3\States\NV\NNHP_DONOTSHARE\TNC_GDE_2019\TNC_GDE_Project_poly.shp"
species_sensitive = r"K:\GIS3\States\NV\NNHP_DONOTSHARE\TNC_GDE_April_2019_DS_poly\TNC_GDE_Project_poly_DS.shp"

# Create copies of the point and line features to buffer
point_copy = arcpy.CopyFeatures_management(species_point, "nnhp_point_copy")
line_copy = arcpy.CopyFeatures_management(species_line, "nnhp_line_copy")
point_buff = arcpy.Buffer_analysis(point_copy, "nnhp_point_buffer", "5 Meters", "FULL")
line_buff = arcpy.Buffer_analysis(line_copy, "nnhp_line_buffer", "5 Meters", "FULL")

# Create single NNHP species layer from the above; Remove the location fields
species_nnhp = arcpy.Merge_management([point_buff, line_buff, species_poly, species_sensitive], "species_nnhp_temp")
arcpy.DeleteField_management(species_nnhp, "REFERENCE_")
arcpy.DeleteField_management(species_nnhp, "REFERENCE1")

# Remove extinct/extirpated species from the list
extirp_list = list()
with arcpy.da.UpdateCursor(species_nnhp, ["S_RANK", "SCOMNAME"]) as cursor:
    for row in cursor:
        if "SX" in str(row[0]):
            print(row[1])
            extirp_list.append(row[1])
            cursor.deleteRow()
            print(row[0])
del cursor
x = set(extirp_list)

# Change 'Juga laurae' to 'Juga acutifilosa'
with arcpy.da.UpdateCursor(species_nnhp, "SNAME") as cursor:
    for row in cursor:
        if str(row[0]) == "Juga laurae":
            row[0] = "Juga acutifilosa"
            cursor.updateRow(row)
            print("Fixing name for Juga acutifilosa")
del cursor

# Create Source code field and populate
arcpy.AddField_management(species_nnhp, "SOURCECODE", "TEXT")
with arcpy.da.UpdateCursor(species_nnhp, ['SOURCECODE']) as cursor:
    for row in cursor:
        row[0] = "nnhp"
        cursor.updateRow(row)
del cursor

#-------------------------------------------------------------------------------
# Create list of unique species from NNHP records

species_nnhp = path + "\\species_nnhp_temp"

species_tbl = arcpy.TableToTable_conversion(species_nnhp, env.workspace, "species_nnhp_tbl")
arcpy.GetCount_management(species_tbl)

# Make list of just species name
species_names = list()
with arcpy.da.SearchCursor(species_tbl, ["SNAME"]) as cursor:
    for row in cursor:
        species_names.append(row[0])
del cursor
len(species_names) # Number of species names in list should = record count
len(set(species_names)) # Use set() to get number of unique species names
unique_names = list(set(species_names))

# Create a table of just the unique species names
unique_species = arcpy.CreateTable_management(out_path = env.workspace, out_name = "species_nnhp_unique")
arcpy.AddField_management(unique_species, "SNAME", "TEXT")
cursor = arcpy.da.InsertCursor(unique_species, ['SNAME'])
for name in unique_names:
    print(name)
    cursor.insertRow([name])
arcpy.GetCount_management(unique_species)

# Join remaining attributes to species name table
all_fields = [f.name for f in arcpy.ListFields(species_tbl)]
join_fields = all_fields[2:]
arcpy.JoinField_management(unique_species, "SNAME", species_tbl, "SNAME", join_fields)

# Read in new Endemism information provided by Eric Miskow
endemism = arcpy.TableToTable_conversion(r"K:\GIS3\Projects\GDE\Geospatial\Geodatabase_Layers\GDE_Species\Endemic_corrections_ESM_NNHP.csv", env.workspace, "nnhp_esm_endemism")

# Join new endemism field to species list; will create another endemism field
arcpy.JoinField_management(unique_species, "SNAME", endemism, "SNAME", ["ENDEMISM"])

# Fill in original endemism field with Eric's endemism values if it is empty
with arcpy.da.UpdateCursor(unique_species, ["SNAME", "ENDEMISM", "ENDEMISM_1"]) as cursor:
    for row in cursor:
        if row[1] is " ":
            row[1] = row[2]
            print("Filling in endemism as {} for {}".format(row[1], row[0]))
            cursor.updateRow(row)
del cursor
arcpy.DeleteField_management(unique_species, "ENDEMISM_1")

#-------------------------------------------------------------------------------
# Count Species from NNHP

# Fill in endemism in spatial dataset using Eric Miskow's table
endemism = r"U:\sarah.byer\Projects\GDE\GDE_Database.gdb\nnhp_esm_endemism"
arcpy.JoinField_management(species_nnhp, "SNAME", endemism, "SNAME", ["ENDEMISM"])
[f.name for f in arcpy.ListFields(species_nnhp)]
with arcpy.da.UpdateCursor(species_nnhp, ["SNAME", "ENDEMISM", "ENDEMISM_1"]) as cursor:
    for row in cursor:
        if row[1] is " ":
            row[1] = row[2]
            print("Filling in endemism as {} for {}".format(row[1], row[0]))
            cursor.updateRow(row)
del cursor

# NNHP Species Count
hex_nnhp_join = arcpy.SpatialJoin_analysis(gde_unit, species_nnhp, "hex_species_join", "JOIN_ONE_TO_MANY", "KEEP_ALL", "", "INTERSECT")
[f.name for f in arcpy.ListFields(hex_nnhp_join)]
hex_nnhp_names = arcpy.Statistics_analysis(hex_nnhp_join, "hex_species_join_names", [["SNAME", "COUNT"]], ["Hex_ID", "SNAME", "ENDEMISM"])
with arcpy.da.UpdateCursor(hex_nnhp_names, ['SNAME']) as cursor: # Delete rows where SNAME is Null (no proper scientific name in the record, or no species in the hexagon)
    for row in cursor:
        if row[0] is None:
            print("Null scientific name")
            cursor.deleteRow()
del cursor 
arcpy.GetCount_management(hex_nnhp_names)

hex_nnhp_count = arcpy.Statistics_analysis(hex_nnhp_names, "hex_nnhp_count", [["SNAME", "COUNT"]], "Hex_ID")
arcpy.JoinField_management(gde_unit, "Hex_ID", hex_nnhp_count, "Hex_ID", ['COUNT_SNAME'])
arcpy.AddField_management(gde_unit, "NNHP_COUNT", "LONG")
with arcpy.da.UpdateCursor(gde_unit, ['COUNT_SNAME', 'NNHP_COUNT']) as cursor:
    for row in cursor:
        if row[0] is None:
            row[1] = 0
            cursor.updateRow(row)
        else:
            row[1] = row[0]
            cursor.updateRow(row)
del cursor


# Count number of unique endemic species per hexagon and join to hex polygon
# Make a table of only endemic species in hexagons
nnhp_endemic = arcpy.Copy_management(hex_nnhp_names, "hex_species_endemic")
with arcpy.da.UpdateCursor(nnhp_endemic, "ENDEMISM") as cursor:
    for row in cursor:
        if row[0] != "Y":
            print("Removing non-endemic species")
            cursor.deleteRow()
del cursor
arcpy.GetCount_management(nnhp_endemic)

nnhp_endemic_count = arcpy.Statistics_analysis(nnhp_endemic, "hex_nnhp_count_endemic", [["SNAME", "COUNT"]], "Hex_ID")
arcpy.JoinField_management(gde_unit, "Hex_ID", nnhp_endemic_count, "Hex_ID", ['COUNT_SNAME'])
arcpy.AddField_management(gde_unit, "COUNT_EN", "LONG")
[f.name for f in arcpy.ListFields(gde_unit)]
with arcpy.da.UpdateCursor(gde_unit, ['COUNT_SNAME_1', 'COUNT_EN']) as cursor:
    for row in cursor:
        if row[0] is None:
            row[1] = 0
            cursor.updateRow(row)
        else:
            row[1] = row[0]
            cursor.updateRow(row)
del cursor

#-------------------------------------------------------------------------------
# Import hexagons (species polygons) to GDE database Species layer

def mapFields(inlayer, infield, mapfield_name, mapfield_alias, mapfield_type):
    fldMap = arcpy.FieldMap()
    fldMap.addInputField(inlayer, infield)
    mapOut = fldMap.outputField
    mapOut.name, mapOut.alias, mapOut.type = mapfield_name, mapfield_alias, mapfield_type
    fldMap.outputField = mapOut
    return fldMap

# Species polygon fc template from the database
species = r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_050919.gdb\Species"

# Map input fields to template fields and append to Species layer
id_map = mapFields(gde_unit, "Hex_ID", "HEX_ID", "Hexagon ID", "LONG")
nnhp_map = mapFields(gde_unit, "NNHP_COUNT", "COUNT_NNHP", "NNHP Species Count", "LONG")
endemic_map = mapFields(gde_unit, "COUNT_EN", "COUNT_EN", "NNHP Endemic Species Count", "LONG")
fldMap_list = [id_map, nnhp_map, endemic_map]
allFldMappings = arcpy.FieldMappings()
for fm in fldMap_list:
    allFldMappings.addFieldMap(fm)
species_poly_append = arcpy.Append_management([gde_unit], species, "NO_TEST", allFldMappings)


# Populate source code (nnhp)
with arcpy.da.UpdateCursor(species_poly_append, ['SOURCE_CODE']) as cursor:
    for row in cursor:
        row[0] = "nnhp"
        cursor.updateRow(row)
del cursor

#-------------------------------------------------------------------------------
# Import species table to GDE database Species_tbl

# Table of unique species with original field names
unique_species = path + "\\species_nnhp_unique"

# GDE species table template with new field names
species_tbl = r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_050919.gdb\Species_tbl"

# Map input fields to template fields
sci_map = mapFields(unique_species, "SNAME", "SCI_NAME", "Scientific Name", "TEXT")
com_map = mapFields(unique_species, "SCOMNAME", "COM_NAME", "Common Name", "TEXT")
major_map = mapFields(unique_species, "MAJORGROUP", "MAJOR_GROUP", "Major Taxonomic Group", "TEXT")
minor_map = mapFields(unique_species, "MINORGROUP", "MINOR_GROUP", "Minor Taxonomic Group", "TEXT")
nvrank_map = mapFields(unique_species, "S_RANK", "NV_RANK", "NV Conservation Status Rank", "TEXT")
grank_map = mapFields(unique_species, "G_RANK", "G_RANK", "Global Conservation Status Rank", "TEXT")
nvstat_map = mapFields(unique_species, "NV_STAT", "NV_STATUS", "NV Protection Status", "TEXT")
esa_map = mapFields(unique_species, "USESA_NV", "ESA_STATUS", "ESA Conservation Status", "TEXT")
blm_map = mapFields(unique_species, "BLM_STAT", "BLM_STATUS", "BLM Conservation Status", "TEXT")
usfs_map = mapFields(unique_species, "USFS_STAT", "USFS_STATUS", "USFS Conservation Status", "TEXT")
nnps_map = mapFields(unique_species, "NNPS_STAT", "NNPS_STATUS", "NNPS Conservation Status", "TEXT")
wap_map = mapFields(unique_species, "WAP2012", "WAP2012", "WAP 2012 Species of Conservation Priority", "TEXT")
end_map = mapFields(unique_species, "ENDEMISM", "ENDEMISM", "Endemism", "TEXT")
nnhp_map = mapFields(unique_species, "NNHP_TRACK", "NNHP_LIST", "NNHP List", "TEXT")
source_map = mapFields(unique_species, "SOURCECODE", "SOURCE_CODE", "Source Code", "TEXT")
fldMap_list = [sci_map, com_map, major_map, minor_map, nvrank_map, grank_map, nvstat_map, esa_map, blm_map, usfs_map, nnps_map, wap_map, end_map, nnhp_map, source_map]
allFldMappings = arcpy.FieldMappings()
for fm in fldMap_list:
    allFldMappings.addFieldMap(fm)
    
# Append species table records to species table template
species_tbl_append = arcpy.Append_management([unique_species], species_tbl, "NO_TEST", allFldMappings)

# END