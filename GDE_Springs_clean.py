#-------------------------------------------------------------------------------
# Name:        NV iGDE Database - Springs
# Purpose:     Process SSI data and add to the Springs layer of the NV iGDE database
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

# Process SSI data

ssi_gdb = r"K:\GIS3\States_WIP\NV\Hydrology\Springs\Nevada_Springs_Apr_21_2019.gdb"
ssi_orig =  r"K:\GIS3\States_WIP\NV\Hydrology\Springs\Nevada_Springs_Apr_21_2019.gdb\Nevada_Springs_Apr_21_2019_Summarized"

# Make a copy of the springs data to process
ssi_copy = arcpy.Copy_management(ssi_orig, "ssi_summarized_copy")

# Add and populate a Source Code field
arcpy.AddField_management(ssi_copy, "SOURCECODE", "TEXT", 20)
with arcpy.da.UpdateCursor(ssi_copy, ["SOURCECODE"]) as cursor:
    for row in cursor:
        row[0] = "ssi"
        cursor.updateRow(row)
del cursor

#-------------------------------------------------------------------------------

# Calculate species data for each spring (number of vert, invert, and plant species observed at each spring)

# """NOTE only species record with Genus and Species allowed to stay"""

# """Vertebrates"""
vert_tbl = ssi_gdb + "\\Nevada_Springs_Apr_21_2019_Summarized_TaxaVert_by_Site"
vert_copy = arcpy.Copy_management(vert_tbl, "ssi_vert_copy")

# Standardize empty genus and species attributes
# Make values 'Null' if length of genus/species name is < 2 or it is already 'Null'
# Genus 
with arcpy.da.UpdateCursor(vert_copy, ['FaunaGenus']) as cursor:
    for row in cursor:
        if (len(str(row[0])) < 2) or (row[0] is None):
            row[0] = None
            cursor.updateRow(row)
        else:
            print("{}".format(row[0]))
del cursor
# Species
with arcpy.da.UpdateCursor(vert_copy, ['FaunaSpecies']) as cursor:
    for row in cursor:
        if (len(str(row[0])) < 2) or (row[0] is None):
            row[0] = None
            cursor.updateRow(row)
        else:
            print("{}".format(row[0]))
del cursor

# Create a new attribute to hold scientific name for the species. FaunaFullName may = order + family + genus + species
# All "empty" rows in the species attribute will be deleted
arcpy.AddField_management(vert_copy, "VertSciName", "TEXT")
with arcpy.da.UpdateCursor(vert_copy, ['FaunaGenus', 'FaunaSpecies', 'VertSciName']) as cursor:
    for row in cursor:
        if row[1] is not None:
        # If Species field has a valid value, populate the sciname field    
            row[2] = str(row[0]) + " " + str(row[1])
            cursor.updateRow(row)
            print(row[2])
        else:
            cursor.deleteRow()
            print("Deleting invalid species record")
del cursor

# Calculate number of valid species observed at springs
vert_tbl_outname = path + "\\SSI_VertCount_tbl"
vert_tbl_sum = arcpy.Statistics_analysis(vert_copy, vert_tbl_outname, [["VertSciName", "COUNT"]], "SiteID")


# """Invertebrates"""
invert_tbl = ssi_gdb + "\\Nevada_Springs_Apr_21_2019_Summarized_TaxaInvert_by_Site"
invert_copy = arcpy.Copy_management(invert_tbl, "ssi_invert_copy")

# Standardize empty genus and species attributes
# Make values 'Null' if length of genus/species name is < 2 or it is already 'Null'
# Genus 
with arcpy.da.UpdateCursor(invert_copy, ['Genus']) as cursor:
    for row in cursor:
        if (len(str(row[0])) < 2) or (row[0] is None):
            row[0] = None
            cursor.updateRow(row)
        else:
            print("{}".format(row[0]))
del cursor
# Species
with arcpy.da.UpdateCursor(invert_copy, ['Species']) as cursor:
    for row in cursor:
        if (len(str(row[0])) < 2) or (row[0] is None):
            row[0] = None
            cursor.updateRow(row)
        else:
            print("{}".format(row[0]))
del cursor

# Create a new attribute to hold scientific name for the species. FullName may = order + family + genus + species
# All "empty" rows in the species attribute will be deleted
arcpy.AddField_management(invert_copy, "InvertSciName", "TEXT")
with arcpy.da.UpdateCursor(invert_copy, ['Genus', 'Species', 'InvertSciName']) as cursor:
    for row in cursor:
        if row[1] is not None:
        # If Species field has a valid value, populate the sciname field    
            row[2] = str(row[0]) + " " + str(row[1])
            cursor.updateRow(row)
            print(row[2])
        else:
            cursor.deleteRow()
            print("Deleting invalid species record")
del cursor

# Calculate number of valid species observed at springs
invert_tbl_outname = path + "\\SSI_InvertCount_tbl"
invert_tbl_sum = arcpy.Statistics_analysis(invert_copy, invert_tbl_outname, [["InvertSciName", "COUNT"]], "SiteID")


# """Plants"""
flora_tbl = ssi_gdb + "\\Nevada_Springs_Apr_21_2019_Summarized_TaxaFlora_by_Site"
flora_copy = arcpy.Copy_management(flora_tbl, "ssi_flora_copy")

# Standardize empty genus and species attributes
# Make values 'Null' if length of genus/species name is < 2 or it is already 'Null'
# Genus 
with arcpy.da.UpdateCursor(flora_copy, ['Genus']) as cursor:
    for row in cursor:
        if (len(str(row[0])) < 2) or (row[0] is None):
            row[0] = None
            cursor.updateRow(row)
        else:
            print("{}".format(row[0]))
del cursor
# Species
with arcpy.da.UpdateCursor(flora_copy, ['Species']) as cursor:
    for row in cursor:
        if (len(str(row[0])) < 2) or (row[0] is None):
            row[0] = None
            cursor.updateRow(row)
        else:
            print("{}".format(row[0]))
del cursor


# Create a new attribute to hold scientific name for the species. FullName may = order + family + genus + species
# Exception made for 4 records that have valid scientific names in the FloraSpecies field, but no data in the Genus or Species fields
# All "empty" rows in the species attribute will be deleted
arcpy.AddField_management(flora_copy, "FloraSciName", "TEXT")
keep_names = ["Philonotis fontana", "Primula fragrans", "Scirpus americanus", "Spirogyra parula"]
with arcpy.da.UpdateCursor(flora_copy, ['Genus', 'Species', 'FloraSciName', 'FloraSpecies']) as cursor:
    for row in cursor:
        if row[1] is not None:
        # If Species field isn't empty, populate the sciname field    
            row[2] = str(row[0]) + " " + str(row[1])
            cursor.updateRow(row)
            #print(row[2])
        elif str(row[3]) in keep_names:
            row[2] = str(row[3])
            cursor.updateRow(row)
            print("Making exception for {}".format(row[3]))
        else:
            cursor.deleteRow()
            print("Deleting invalid species record")
del cursor

# Calculate number of valid species observed at springs
flora_tbl_outname = path + "\\SSI_FloraCount_tbl"
flora_tbl_sum = arcpy.Statistics_analysis(flora_copy, flora_tbl_outname, [["FloraSciName", "COUNT"]], "SiteID")

# Join calculated species fields from tables to the SSI dataset by Site ID
arcpy.JoinField_management(ssi_copy, "SiteID", vert_tbl_sum, "SiteID", "COUNT_VertSciName")
arcpy.JoinField_management(ssi_copy, "SiteID", invert_tbl_sum, "SiteID", "COUNT_InvertSciName")
arcpy.JoinField_management(ssi_copy, "SiteID", flora_tbl_sum, "SiteID", "COUNT_FloraSciName")
[f.name for f in arcpy.ListFields(ssi_copy)]

# Don't replace Nulls in species count records with zeroes
# Zero gives potentially false perception that there are no species at that springs, when in reality it may have not been surveyed for species

#-------------------------------------------------------------------------------

# Remove records where INV_STAT = No spring
# Spring lcoation was visited but no spring was present
with arcpy.da.UpdateCursor(ssi_copy, ["InventoryLevel"]) as cursor:
    for row in cursor:
        if str(row[0]) == "No Spring" or str(row[0]) == "NoSpring":
            cursor.deleteRow()
            print("Deleting false spring record")
del cursor

#-------------------------------------------------------------------------------

# Add springs to iGDE Springs layer
gde_springs = r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_050919.gdb\Springs"

# Map to iGDE Springs layer and put point features there
def mapFields(inlayer, infield, mapfield_name, mapfield_alias, mapfield_type): # mapFields function
    fldMap = arcpy.FieldMap()
    fldMap.addInputField(inlayer, infield)
    mapOut = fldMap.outputField
    mapOut.name, mapOut.alias, mapOut.type = mapfield_name, mapfield_alias, mapfield_type
    fldMap.outputField = mapOut
    return fldMap

# Field mapping for Springs (from SSI to GDE Springs)
source_map = mapFields(ssi_copy, "SOURCECODE", "SOURCE_CODE", "Source Code", "TEXT")
spring_id_map = mapFields(ssi_copy, "SiteID", "SPRING_ID", "Spring ID", "LONG")
spring_name_map = mapFields(ssi_copy, "ShortName", "SPRING_NAME", "Spring Name", "TEXT")
spring_type1_map = mapFields(ssi_copy, "SpringType1", "SPRING_TYPE1", "Spring Type 1", "TEXT")
spring_type2_map = mapFields(ssi_copy, "SpringType2", "SPRING_TYPE2", "Spring Type 2", "TEXT")
image_link_map = mapFields(ssi_copy, "CastImageHyperlink", "IMAGE_LINK", "Image Hyperlink", "TEXT")
sketch_link_map = mapFields(ssi_copy, "CastSketchHyperlink", "SKECTH_LINK", "Sketch Hyperlink", "TEXT")
lat_map = mapFields(ssi_copy, "LatitudeDD", "LATITUDE", "Latitude", "DOUBLE")
long_map = mapFields(ssi_copy, "LongitudeDD", "LONGITUDE", "Longitude", "DOUBLE")
elev_map = mapFields(ssi_copy, "ElevationM", "ELEVATION", "Elevation (m)", "DOUBLE")
inv_stat_map = mapFields(ssi_copy, "InventoryLevel", "INV_STAT", "Inventory Status", "TEXT")
surv_count_map = mapFields(ssi_copy, "SurveyCount", "SURV_COUNT", "Survey Count", "SHORT")
flow_map = mapFields(ssi_copy, "Flow_Mean", "FLOW_MEAN", "Flow Mean (L/s)", "DOUBLE")
ph_map = mapFields(ssi_copy, "pH_Mean", "PH_MEAN", "pH Mean", "DOUBLE")
temp_map = mapFields(ssi_copy, "Water_Temp_Mean", "WATER_TEMP_MEAN", "Water Temperature Mean (C)", "DOUBLE")
spec_map = mapFields(ssi_copy, "Spec_Cond_Mean", "SPEC_COND_MEAN", "Specific Conductance Mean (uS/cm)", "DOUBLE")
alk_map = mapFields(ssi_copy, "Alkalinity_Mean", "ALKALINITY_MEAN", "Alkalinity Mean (mg/L)", "DOUBLE")
area_map = mapFields(ssi_copy, "TotalAreaSQM", "SPRING_AREA", "Spring Area (m2)", "DOUBLE")
vert_ct_map = mapFields(ssi_copy, "COUNT_VertSciName", "VERT_COUNT", "Vertebrate Species Count", "LONG") # Calculated
invert_ct_map = mapFields(ssi_copy, "COUNT_InvertSciName", "INVERT_COUNT", "Invertebrate Species Count", "LONG") # Calculated
flora_ct_map = mapFields(ssi_copy, "COUNT_FloraSciName", "FLORA_COUNT", "Plant Species Count", "LONG") # Calculated

maplist = [source_map, spring_id_map, spring_name_map, 
           spring_type1_map, spring_type2_map, image_link_map, 
           sketch_link_map, lat_map, long_map, 
           elev_map, inv_stat_map, surv_count_map, 
           flow_map, ph_map, temp_map, 
           spec_map, alk_map, area_map, 
           vert_ct_map, invert_ct_map, flora_ct_map]
springFldMappings = arcpy.FieldMappings()
for fm in maplist:
    springFldMappings.addFieldMap(fm)

# Append to GDE database Wetland layer
arcpy.Append_management(ssi_copy, gde_springs, "NO_TEST", springFldMappings)

# END