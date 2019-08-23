#-------------------------------------------------------------------------------
# Name:        NV iGDE Database - Story Map summary layers
# Purpose:     Creates the summary layers to be made publicly available in the story map
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
# Select the area unit that will be used to summarize: hexagons or hydro basins

# """NOTE - switch the area unit between hexagons or hydrographic basins"""
#area_unit = r"K:\GIS3\Projects\GDE\Geospatial\Geodatabase_Layers\GDE_Boundaries\nv_chat_polygons.shp"
area_unit = r"K:\GIS3\Projects\GDE\Geospatial\Geodatabase_Layers\GDE_Boundaries\NDWR_HydroBasins.shp"

# Make a copy of the area unit; this will be used to contain the summary attributes
for fc in [1]:
    fields = arcpy.ListFields(area_unit)
    print([f.name for f in fields])
    area_unit_fields = list([f.name for f in fields])
    if "Hex_ID" in area_unit_fields:
        print("Copying hexagon features")
        gde_unit = arcpy.CopyFeatures_management(area_unit, "hexagon_units") # HEXAGONS
        # Calculate shape area of the unit features
        arcpy.AddField_management(gde_unit, "POLY_AREA", "DOUBLE")
        arcpy.CalculateGeometryAttributes_management(gde_unit, [["POLY_AREA", "AREA"]], "", "ACRES", env.outputCoordinateSystem)
        gde_unit = path + "\\hexagon_units"
    else:
        print("Copying hydrographic basin features")
        gde_unit = arcpy.CopyFeatures_management(area_unit, "hydrobasin_units") # HYDRO BASINS
        # Calculate shape area of the unit features
        arcpy.AddField_management(gde_unit, "POLY_AREA", "DOUBLE")
        arcpy.CalculateGeometryAttributes_management(gde_unit, [["POLY_AREA", "AREA"]], "", "ACRES", env.outputCoordinateSystem)
        gde_unit = path + "\\hydrobasin_units"
        


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Phreatophytes Summary
# Percent of each area unit that contains phreatophytes
# Percent of each area unit that is forest/meadow/shrub phreatophyte

# Load Vegetation layer
phreatophytes = r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_050919.gdb\Phreatophytes"

# Calculate area of each unit that has phreatophyte features
# Dissolve phreatophytes, then intersect with summarizing unit, then dissolve again by intersecting unit
ph_dissolve = arcpy.Dissolve_management(phreatophytes, "ph_dissolve")
ph_chunk = arcpy.Intersect_analysis([ph_dissolve, gde_unit], "ph_chunk")

# Dissolve by Hex_ID or HYD_AREA
gde_unit_fields = list([f.name for f in arcpy.ListFields(gde_unit)])
if "Hex_ID" in gde_unit_fields:
    print("Dissolving by hexagons")
    ph_int = arcpy.Dissolve_management(ph_chunk, "ph_int", "Hex_ID") # HEXAGONS
else:
    print("Dissolving by hydrographic basins")
    ph_int = arcpy.Dissolve_management(ph_chunk, "ph_int", "HYD_AREA") # HYDRO BASINS 

# Phreatophytes are "chopped" by the hexagons they fall in, OR
# Phreatophytes are "clumped" by the HYD_AREA they fall into
    
# Join POLY_AREA back to intersected feature by HYD_AREA/Hex_ID (need original feature area attached)
if "hexagon" in str(gde_unit):
    print("Joining hexagon POLY_AREA")
    arcpy.JoinField_management(ph_int, "Hex_ID", gde_unit, "Hex_ID", ["POLY_AREA"])
else:
    print("Joining hydro basin POLY_AREA")
    arcpy.JoinField_management(ph_int, "HYD_AREA", gde_unit, "HYD_AREA", ["POLY_AREA"])

# Calculate area of each phreatophyte chunk
arcpy.AddField_management(ph_int, "AREA_PHR", "DOUBLE") 
arcpy.CalculateGeometryAttributes_management(ph_int, [["AREA_PHR", "AREA"]], "", "ACRES", env.outputCoordinateSystem)

# Calculate percent of each summarizing unit that is phreatophyte
arcpy.AddField_management(ph_int, "PER_PHR", "DOUBLE") 
arcpy.CalculateField_management(ph_int, "PER_PHR", '100*(!AREA_PHR!/!POLY_AREA!)', "PYTHON3")


# Calculate area of each unit that has forest, shrubland, or unknown features
# Dissolve by phreatophyte groups
ph_types = arcpy.Dissolve_management(phreatophytes, "ph_type_dissolve", ["PHR_GROUP"])

# Isolate forests, shrublands, and unknown groups in different feature classes
forests = arcpy.Copy_management(ph_types, "forests_dissolve")
with arcpy.da.UpdateCursor(forests, ['PHR_GROUP']) as cursor:
    for row in cursor:
        if row[0] != "Forest":
            print("Deleting non-forest features")
            cursor.deleteRow()
del cursor
shrubs = arcpy.Copy_management(ph_types, "shrubs_dissolve")
with arcpy.da.UpdateCursor(shrubs, ['PHR_GROUP']) as cursor:
    for row in cursor:
        if row[0] != "Shrubland":
            print("Deleting non-shrubland features")
            cursor.deleteRow()
del cursor
unknown = arcpy.Copy_management(ph_types, "unknown_dissolve")
with arcpy.da.UpdateCursor(unknown, ['PHR_GROUP']) as cursor:
    for row in cursor:
        if row[0] != "Unknown":
            print("Deleting non-unknown features")
            cursor.deleteRow()
del cursor

# Intersect forests with summarizing unit to get areas/percent covers
forests_chunk = arcpy.Intersect_analysis([forests, gde_unit], "forests_chunk")
if "hexagon" in str(gde_unit):
    print("Processing forests in hexagons")
    forests_int = arcpy.Dissolve_management(forests_chunk, "forests_intersect", "Hex_ID")
    arcpy.JoinField_management(forests_int, "Hex_ID", gde_unit, "Hex_ID", ["POLY_AREA"])
else:
    print("Processing forests in hydro basins")
    forests_int = arcpy.Dissolve_management(forests_chunk, "forests_intersect", "HYD_AREA")
    arcpy.JoinField_management(forests_int, "HYD_AREA", gde_unit, "HYD_AREA", ["POLY_AREA"])
    
arcpy.AddField_management(forests_int, "AREA_FRST", "DOUBLE") 
arcpy.CalculateGeometryAttributes_management(forests_int, [["AREA_FRST", "AREA"]], "", "ACRES", env.outputCoordinateSystem)
arcpy.AddField_management(forests_int, "PER_FRST", "DOUBLE") 
arcpy.CalculateField_management(forests_int, "PER_FRST", '100*(!AREA_FRST!/!POLY_AREA!)', "PYTHON3")

# Intersect shrubs with summarizing unit to get areas/percent covers
shrubs_chunk = arcpy.Intersect_analysis([shrubs, gde_unit], "shrubs_chunk")
if "hexagon" in str(gde_unit):
    print("Processing shrubs in hexagons")
    shrubs_int = arcpy.Dissolve_management(shrubs_chunk, "shrubs_intersect", "Hex_ID")
    arcpy.JoinField_management(shrubs_int, "Hex_ID", gde_unit, "Hex_ID", ["POLY_AREA"])
else:
    print("Processing shrubs in hydro basins")
    shrubs_int = arcpy.Dissolve_management(shrubs_chunk, "shrubs_intersect", "HYD_AREA")
    arcpy.JoinField_management(shrubs_int, "HYD_AREA", gde_unit, "HYD_AREA", ["POLY_AREA"])
    
arcpy.AddField_management(shrubs_int, "AREA_SHRUB", "DOUBLE") 
arcpy.CalculateGeometryAttributes_management(shrubs_int, [["AREA_SHRUB", "AREA"]], "", "ACRES", env.outputCoordinateSystem)
arcpy.AddField_management(shrubs_int, "PER_SHRUB", "DOUBLE") 
arcpy.CalculateField_management(shrubs_int, "PER_SHRUB", '100*(!AREA_SHRUB!/!POLY_AREA!)', "PYTHON3")

# Intersect unknown features with summarizing unit to get areas/percent covers
unknown_chunk = arcpy.Intersect_analysis([unknown, gde_unit], "unknown_chunk")
if "hexagon" in str(gde_unit):
    print("Processing unknown features in hexagons")
    unknown_int = arcpy.Dissolve_management(unknown_chunk, "unknown_intersect", "Hex_ID")
    arcpy.JoinField_management(unknown_int, "Hex_ID", gde_unit, "Hex_ID", ["POLY_AREA"])
else:
    print("Processing unknown features in hydro basins")
    unknown_int = arcpy.Dissolve_management(unknown_chunk, "unknown_intersect", "HYD_AREA")
    arcpy.JoinField_management(unknown_int, "HYD_AREA", gde_unit, "HYD_AREA", ["POLY_AREA"])

arcpy.AddField_management(unknown_int, "AREA_UNK", "DOUBLE") 
arcpy.CalculateGeometryAttributes_management(unknown_int, [["AREA_UNK", "AREA"]], "", "ACRES", env.outputCoordinateSystem)
arcpy.AddField_management(unknown_int, "PER_UNK", "DOUBLE") 
arcpy.CalculateField_management(unknown_int, "PER_UNK", '100*(!AREA_UNK!/!POLY_AREA!)', "PYTHON3")

# Paths to processed features above 
ph_int = path + "\\ph_int"
forests_int = path + "\\forests_intersect"
shrubs_int = path + "\\shrubs_intersect"
unknown_int = path + "\\unknown_intersect"

# Join new calculated area fields from intersect layers to full gde unit layer
for fc in [1]:
    unit_fields = arcpy.ListFields(gde_unit)
    print([f.name for f in unit_fields])
    unit_fields = list([f.name for f in unit_fields])
    if "Hex_ID" in unit_fields:
        print("Joining new geoemetry fields to hexagon features by Hex_ID")
        arcpy.JoinField_management(gde_unit, 'Hex_ID', ph_int, 'Hex_ID', ["AREA_PHR", "PER_PHR"])
        arcpy.JoinField_management(gde_unit, 'Hex_ID', forests_int, 'Hex_ID', ["AREA_FRST", "PER_FRST"])
        arcpy.JoinField_management(gde_unit, 'Hex_ID', shrubs_int, 'Hex_ID', ["AREA_SHRUB", "PER_SHRUB"])
        arcpy.JoinField_management(gde_unit, 'Hex_ID', unknown_int, 'Hex_ID', ["AREA_UNK", "PER_UNK"])
    else:
        print("Joining new geometry fields to hydrographic basin features by HYD_AREA")
        arcpy.JoinField_management(gde_unit, 'HYD_AREA', ph_int, 'HYD_AREA', ["AREA_PHR", "PER_PHR"])
        arcpy.JoinField_management(gde_unit, 'HYD_AREA', forests_int, 'HYD_AREA', ["AREA_FRST", "PER_FRST"])
        arcpy.JoinField_management(gde_unit, 'HYD_AREA', shrubs_int, 'HYD_AREA', ["AREA_SHRUB", "PER_SHRUB"])
        arcpy.JoinField_management(gde_unit, 'HYD_AREA', unknown_int, 'HYD_AREA', ["AREA_UNK", "PER_UNK"])

# Make sure all values that may be null are reclassified to 0
ph_fields = ["AREA_PHR", "PER_PHR", "AREA_FRST", "PER_FRST", "AREA_SHRUB", "PER_SHRUB", "AREA_UNK", "PER_UNK"]
for field in ph_fields:
    with arcpy.da.UpdateCursor(gde_unit, field) as cursor:
        for row in cursor:
            if row[0] is None:
                row[0] = 0
                cursor.updateRow(row)
    del cursor

# Make sure all PERCENT values are < 100
ph_fields = ["PER_PHR", "PER_FRST", "PER_SHRUB", "PER_UNK"]
for field in ph_fields:
    with arcpy.da.UpdateCursor(gde_unit, field) as cursor:
        for row in cursor:
            if row[0] > 100:
                row[0] = 100
                cursor.updateRow(row)            
    del cursor
    
# Phreatophyte summary fields are "AREA_PHR", "PER_PHR", "AREA_FRST", "PER_FRST", "AREA_SHRUB", "PER_SHRUB", "AREA_UNK", "PER_UNK"
    
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Wetlands Summary
# Percent of each area unit that contains Wetlands

# Select a new GDE summarizing area unit, or keep the same 
#gde_unit = gdb_path + "\\hexagon_units"
#gde_unit = gdb_path + "\\hydrobasin_units"
    
# Load Wetlands layer
wetlands = r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_050919.gdb\Wetlands"

# Calculate area of each unit that has wetland features
# Dissolve phreatophytes, then intersect with summarizing unit
wet_dissolve = arcpy.Dissolve_management(wetlands, "wet_dissolve")
wet_chunk = arcpy.Intersect_analysis([wet_dissolve, gde_unit], "wet_chunk")

if "hexagon" in str(gde_unit):
    print("Dissolving wetlands by hexagon and joining POLY_AREA")
    wet_int = arcpy.Dissolve_management(wet_chunk, "wet_int", "Hex_ID")
    arcpy.JoinField_management(wet_int, "Hex_ID", gde_unit, "Hex_ID", ["POLY_AREA"])    
else:
    print("Dissolving wetlands by hydro basin and joining POLY_AREA")
    wet_int = arcpy.Dissolve_management(wet_chunk, "wet_int", "HYD_AREA")
    arcpy.JoinField_management(wet_int, "HYD_AREA", gde_unit, "HYD_AREA", ["POLY_AREA"])

# Wetlands are "chopped" by the hexagons they fall in, OR
# Wetlands are "clumped" by the HYD_AREA they fall into

# Calculate area of each wetland chunk
arcpy.AddField_management(wet_int, "AREA_WET", "DOUBLE") 
arcpy.CalculateGeometryAttributes_management(wet_int, [["AREA_WET", "AREA"]], "", "ACRES", env.outputCoordinateSystem)

# Calculate percent of each summarizing unit that is wetland
arcpy.AddField_management(wet_int, "PER_WET", "DOUBLE") 
arcpy.CalculateField_management(wet_int, "PER_WET", '100*(!AREA_WET!/!POLY_AREA!)', "PYTHON3")

# Join new calculated area fields to full gde unit layer
for fc in [1]:
    wet_fields = arcpy.ListFields(wet_int)
    print([f.name for f in wet_fields])
    wet_fields = list([f.name for f in wet_fields])
    if "Hex_ID" in wet_fields:
        print("Joining new wetland fields to hexagon features by Hex_ID")
        arcpy.JoinField_management(gde_unit, 'Hex_ID', wet_int, 'Hex_ID', ["AREA_WET"])
        arcpy.JoinField_management(gde_unit, 'Hex_ID', wet_int, 'Hex_ID', ["PER_WET"])
    else:
        print("Joining new wetland fields to hydrographic basin features by HYD_AREA")
        arcpy.JoinField_management(gde_unit, 'HYD_AREA', wet_int, 'HYD_AREA', ["AREA_WET"])
        arcpy.JoinField_management(gde_unit, 'HYD_AREA', wet_int, 'HYD_AREA', ["PER_WET"])
        
# Make sure all values that may be null (no wetlands) are reclassified to 0
wet_fields = ["AREA_WET", "PER_WET"]
for field in wet_fields:
    with arcpy.da.UpdateCursor(gde_unit, field) as cursor:
        for row in cursor:
            if row[0] is None:
                row[0] = 0
                cursor.updateRow(row)
    del cursor

# Make sure all PERCENT values are < 100
wet_fields = ["PER_WET"]
for field in wet_fields:
    with arcpy.da.UpdateCursor(gde_unit, field) as cursor:
        for row in cursor:
            if row[0] > 100:
                row[0] = 100
                cursor.updateRow(row)
    del cursor    
    
    
# 'PER_WET' and 'AREA_WET' field contains the summary data for this layer
    
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Spring Summary
# Number of springs in each area unit

# Load Springs data
springs = r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_050919.gdb\Springs"

# Spatial join springs to area unit
 # Creates a "copy" of each area unit where there is at least 1 spring in a unit
unit_springs = arcpy.SpatialJoin_analysis(gde_unit, springs, "temp_join_units_springs", "JOIN_ONE_TO_MANY", "KEEP_ALL", "", "INTERSECT")

# Count number of times a feature has a source code (number of springs) by the unit's ID
for fc in [1]:
    fields = arcpy.ListFields(unit_springs)
    print([f.name for f in fields])
    fields = list([f.name for f in fields])
    if "Hex_ID" in fields:
        print("Counting number of springs in hexagons")
        unit_springs_count = arcpy.Statistics_analysis(unit_springs, "join_units_springs_count", [["SOURCE_CODE", "COUNT"]], ["Hex_ID"])
    else:
        print("Counting number of springs in hydrographic basins")
        unit_springs_count = arcpy.Statistics_analysis(unit_springs, "join_units_springs_count", [["SOURCE_CODE", "COUNT"]], ["HYD_AREA"])

# Calculate number of springs per unit in the table
arcpy.AddField_management(unit_springs_count, "COUNT_SPR", "LONG")
arcpy.CalculateField_management(unit_springs_count, 'COUNT_SPR', "!COUNT_SOURCE_CODE!", "PYTHON3")
with arcpy.da.UpdateCursor(unit_springs_count, ["COUNT_SPR"]) as cursor: # Null values become 0
    for row in cursor:
        if row[0] == None:
            print("updating null value to 0")
            row[0] = 0
            cursor.updateRow(row)
del cursor

# Join 'COUNT_SPR' to the main unit feature class
for fc in [1]:
    fields = arcpy.ListFields(gde_unit)
    print([f.name for f in fields])
    fields = list([f.name for f in fields])
    if "Hex_ID" in fields:
        print("Adding spring count field to hexagon layer")
        arcpy.JoinField_management(gde_unit, "Hex_ID", unit_springs_count, "Hex_ID", ["COUNT_SPR"])
    else:
        print("Adding spring summary fields to hydrographic basin layer")
        arcpy.JoinField_management(gde_unit, "HYD_AREA", unit_springs_count, "HYD_AREA", ["COUNT_SPR"])

# Calculate springs per acre - only for hydro basins!
arcpy.AddField_management(gde_unit, "AREA_SPR", "DOUBLE")
arcpy.CalculateField_management(gde_unit, "AREA_SPR", "!COUNT_SPR!/!POLY_AREA!", "PYTHON3")


# 'COUNT_SPR' and 'AREA_SPR' contains the summary data for this layer

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Lake/Playa Summary
# Percent of each area unit that contains Lakes/Playas

# Load Lakes/Playas layer
lakes_playas = r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_050919.gdb\Lakes_Playas"

# Calculate area of each unit that has lake/playa features
# Dissolve lakes/playas, then intersect with summarizing unit
lp_dissolve = arcpy.Dissolve_management(lakes_playas, "lp_dissolve")
lp_chunk = arcpy.Intersect_analysis([lp_dissolve, gde_unit], "lp_chunk")

if "hexagon" in str(gde_unit):
    print("Dissolving lakes/playas by hexagon and joining POLY_AREA")
    lp_int = arcpy.Dissolve_management(lp_chunk, "lp_int", "Hex_ID")
    arcpy.JoinField_management(lp_int, "Hex_ID", gde_unit, "Hex_ID", ["POLY_AREA"]) 
else:
    print("Dissolving lakes/playas by hydro basin and joining POLY_AREA")
    lp_int = arcpy.Dissolve_management(lp_chunk, "lp_int", "HYD_AREA")
    arcpy.JoinField_management(lp_int, "HYD_AREA", gde_unit, "HYD_AREA", ["POLY_AREA"])

# Calculate area of each lake/playa chunk
arcpy.AddField_management(lp_int, "AREA_LKPL", "DOUBLE") 
arcpy.CalculateGeometryAttributes_management(lp_int, [["AREA_LKPL", "AREA"]], "", "ACRES", env.outputCoordinateSystem)

# Calculate percent of each summarizing unit that is lake/playa
arcpy.AddField_management(lp_int, "PER_LKPL", "DOUBLE") 
arcpy.CalculateField_management(lp_int, "PER_LKPL", '100*(!AREA_LKPL!/!POLY_AREA!)', "PYTHON3")


# Calculate area of each unit that has lakes vs. playa features
# Dissolve by body type
lp_types = arcpy.Dissolve_management(lakes_playas, "lp_type_dissolve", ["BODY_TYPE"])
# Isolate lakes and Playas in different feature classes
lakes = arcpy.Copy_management(lp_types, "lakes_dissolve")
with arcpy.da.UpdateCursor(lakes, ['BODY_TYPE']) as cursor:
    for row in cursor:
        if row[0] != "Lake":
            print("Deleting non-Lake features")
            cursor.deleteRow()
del cursor
playas = arcpy.Copy_management(lp_types, "playas_dissolve")
with arcpy.da.UpdateCursor(playas, ["BODY_TYPE"]) as cursor:
    for row in cursor:
        if row[0] != "Playa":
            cursor.deleteRow()
del cursor


# Intersect lakes with summarizing unit to get areas/percent covers
lakes_chunk = arcpy.Intersect_analysis([lakes, gde_unit], "lakes_chunk")
if "hexagon" in str(gde_unit):
    print("Processing lakes in hexagons")
    lakes_int = arcpy.Dissolve_management(lakes_chunk, "lakes_int", "Hex_ID")
    arcpy.JoinField_management(lakes_int, "Hex_ID", gde_unit, "Hex_ID", ["POLY_AREA"])
else:
    print("processing lakes in hydro basins")
    lakes_int = arcpy.Dissolve_management(lakes_chunk, "lakes_int", "HYD_AREA")
    arcpy.JoinField_management(lakes_int, "HYD_AREA", gde_unit, "HYD_AREA", ["POLY_AREA"])

arcpy.AddField_management(lakes_int, "AREA_LAKE", "DOUBLE") 
arcpy.CalculateGeometryAttributes_management(lakes_int, [["AREA_LAKE", "AREA"]], "", "ACRES", env.outputCoordinateSystem)
arcpy.AddField_management(lakes_int, "PER_LAKE", "DOUBLE") 
arcpy.CalculateField_management(lakes_int, "PER_LAKE", '100*(!AREA_LAKE!/!POLY_AREA!)', "PYTHON3")

# Intersect playas with summarizing unit to get areas/percent covers
playas_chunk = arcpy.Intersect_analysis([playas, gde_unit], "playas_chunk")
if "hexagon" in str(gde_unit):
    print("Processing playas in hexagons")
    playas_int = arcpy.Dissolve_management(playas_chunk, "playa_int", "Hex_ID")
    arcpy.JoinField_management(playas_int, "Hex_ID", gde_unit, "Hex_ID", ["POLY_AREA"])
else:
    print("processing playas in hydro basins")
    playas_int = arcpy.Dissolve_management(playas_chunk, "playas_int", "HYD_AREA")
    arcpy.JoinField_management(playas_int, "HYD_AREA", gde_unit, "HYD_AREA", ["POLY_AREA"])

arcpy.AddField_management(playas_int, "AREA_PLAYA", "DOUBLE") 
arcpy.CalculateGeometryAttributes_management(playas_int, [["AREA_PLAYA", "AREA"]], "", "ACRES", env.outputCoordinateSystem)
arcpy.AddField_management(playas_int, "PER_PLAYA", "DOUBLE") 
arcpy.CalculateField_management(playas_int, "PER_PLAYA", '100*(!AREA_PLAYA!/!POLY_AREA!)', "PYTHON3")


# Join new calculated area field from erase layer to full gde unit layer
for fc in [1]:
    unit_fields = arcpy.ListFields(gde_unit)
    print([f.name for f in unit_fields])
    unit_fields = list([f.name for f in unit_fields])
    if "Hex_ID" in unit_fields:
        print("Joining new geoemetry fields to hexagon features by Hex_ID")
        arcpy.JoinField_management(gde_unit, 'Hex_ID', lp_int, 'Hex_ID', ["AREA_LKPL", "PER_LKPL"])
        arcpy.JoinField_management(gde_unit, 'Hex_ID', lakes_int, 'Hex_ID', ["AREA_LAKE", "PER_LAKE"])
        arcpy.JoinField_management(gde_unit, 'Hex_ID', playas_int, 'Hex_ID', ["AREA_PLAYA", "PER_PLAYA"])
    else:
        print("Joining new geometry fields to hydrographic basin features by HYD_AREA")
        arcpy.JoinField_management(gde_unit, 'HYD_AREA', lp_int, 'HYD_AREA', ["AREA_LKPL", "PER_LKPL"])
        arcpy.JoinField_management(gde_unit, 'HYD_AREA', lakes_int, 'HYD_AREA', ["AREA_LAKE", "PER_LAKE"])
        arcpy.JoinField_management(gde_unit, 'HYD_AREA', playas_int, 'HYD_AREA', ["AREA_PLAYA", "PER_PLAYA"])
[f.name for f in arcpy.ListFields(gde_unit)]

# Make sure all values that may be null are reclassified to 0
lp_fields = ["AREA_LKPL", "PER_LKPL", "AREA_LAKE", "PER_LAKE", "AREA_PLAYA", "PER_PLAYA"]
for field in lp_fields:
    with arcpy.da.UpdateCursor(gde_unit, field) as cursor:
        for row in cursor:
            if row[0] is None:
                row[0] = 0
                cursor.updateRow(row)
    del cursor
    
# Make sure all PERCENT values are < 100
lp_fields = ["PER_LKPL", "PER_LAKE", "PER_PLAYA"]
for field in lp_fields:
    with arcpy.da.UpdateCursor(gde_unit, field) as cursor:
        for row in cursor:
            if row[0] > 100:
                row[0] = 100
                cursor.updateRow(row)
    del cursor  

# Lake/playa summary fields are "AREA_LKPL", "PER_LKPL", "AREA_LAKE", "PER_LAKE", "AREA_PLAYA", "PER_PLAYA"
    
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Rivers Summary
# Presence/absence of Rivers in area unit; length of rivers/streams in the unit

# Load river data
rivers = r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_050919.gdb\Rivers_Streams"

# Dissolve rivers to simplify processing
rivers_dissolve = arcpy.Dissolve_management(rivers, "dissolve_rivers")

# Intersect river lines with units
rivers_chunk = arcpy.Intersect_analysis([rivers_dissolve, gde_unit], "rivers_chunk", "ALL", "", "LINE")
if "hexagon" in str(gde_unit):
    print("Processing rivers in hexagons")
    rivers_int = arcpy.Dissolve_management(rivers_chunk, "rivers_int", "Hex_ID")
    arcpy.JoinField_management(rivers_int, "Hex_ID", gde_unit, "Hex_ID", ["POLY_AREA"])
else:
    print("processing rivers in hydro basins")
    rivers_int = arcpy.Dissolve_management(rivers_chunk, "rivers_int", "HYD_AREA")
    arcpy.JoinField_management(rivers_int, "HYD_AREA", gde_unit, "HYD_AREA", ["POLY_AREA"])

# Calculate sum of miles of rivers in each unit
arcpy.AddField_management(rivers_int, "MILES_RVST", "DOUBLE")
arcpy.CalculateGeometryAttributes_management(rivers_int, [["MILES_RVST", "LENGTH"]], "MILES_US", "", env.outputCoordinateSystem)
arcpy.GetCount_management(rivers_int) # Not all basins/hexagons will have rivers

# Calculate miles of rivers per acre in each unit - hydro basin only!
arcpy.AddField_management(rivers_int, "AREA_RVST", "DOUBLE") 
arcpy.CalculateField_management(rivers_int, "AREA_RVST", '!MILES_RVST!/!POLY_AREA!', "PYTHON3")

# Join 'MILES_RIVST' to the main unit feature class
for fc in [1]:
    fields = arcpy.ListFields(gde_unit)
    print([f.name for f in fields])
    fields = list([f.name for f in fields])
    if "Hex_ID" in fields:
        print("Adding rivers fields field to hexagon layer")
        arcpy.JoinField_management(gde_unit, "Hex_ID", rivers_int, "Hex_ID", ["MILES_RVST"])
       # arcpy.JoinField_management(gde_unit, "Hex_ID", rivers_int, "Hex_ID", ["AREA_RVST"])
    else:
        print("Adding MILES_RIVST field and AREA_RIVST to hydrographic basin layer")
        arcpy.JoinField_management(gde_unit, "HYD_AREA", rivers_int, "HYD_AREA", ["MILES_RVST"])
        arcpy.JoinField_management(gde_unit, "HYD_AREA", rivers_int, "HYD_AREA", ["AREA_RVST"])

# Make sure all values that may be null (no rivers/streams) are reclassified to 0
rs_fields = ["MILES_RVST", "AREA_RVST"]
for field in rs_fields:
    with arcpy.da.UpdateCursor(gde_unit, field) as cursor:
        for row in cursor:
            if row[0] is None:
                row[0] = 0
                cursor.updateRow(row)
    del cursor

# MILES_RVST and AREA_RVST

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Calculate GDE Presence/Score
# Count number of physical GDE features presence in each unit (hexagon/hydro basin)

arcpy.AddField_management(gde_unit, "GDE_COUNT", "LONG")
with arcpy.da.UpdateCursor(gde_unit, ['PER_PHR', 'GDE_COUNT']) as cursor:
    for row in cursor:
        if row[0] > 0:
            row[1] = 1
            cursor.updateRow(row)
        else:
            row[1] = 0
            cursor.updateRow(row)
del cursor
with arcpy.da.UpdateCursor(gde_unit, ['PER_WET', 'GDE_COUNT']) as cursor:
    for row in cursor:
        if row[0] > 0:
            row[1] = row[1] + 1
            cursor.updateRow(row)
        else:
            row[1] = row[1] + 0
            cursor.updateRow(row)
del cursor
with arcpy.da.UpdateCursor(gde_unit, ['COUNT_SPR', 'GDE_COUNT']) as cursor:
    for row in cursor:
        if row[0] > 0:
            row[1] = row[1] + 1
            cursor.updateRow(row)
        else:
            row[1] = row[1] + 0
            cursor.updateRow(row)
del cursor        
with arcpy.da.UpdateCursor(gde_unit, ['PER_LKPL', 'GDE_COUNT']) as cursor:
    for row in cursor:
        if row[0] > 0:
            row[1] = row[1] + 1
            cursor.updateRow(row)
        else:
            row[1] = row[1] + 0
            cursor.updateRow(row)
del cursor
with arcpy.da.UpdateCursor(gde_unit, ['MILES_RVST', 'GDE_COUNT']) as cursor:
    for row in cursor:
        if row[0] > 0:
            row[1] = row[1] + 1
            cursor.updateRow(row)
        else:
            row[1] = row[1] + 0
            cursor.updateRow(row)
del cursor

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# When both hexagons and hydro basins have been processed, add feature classes to the Story Map GDB

arcpy.CreateFileGDB_management(r"K:\GIS3\Projects\GDE\Geospatial", "NV_iGDE_Story_061719")
gdb = r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_Story_061719.gdb"
env.workspace = gdb
arcpy.ListFeatureClasses()

# Copy hexagon and hydrobasin feature classes to th enew geodatabase
hexagons = path + "\\hexagon_units"
hydrobasins = path + "\\hydrobasin_units"
arcpy.CopyFeatures_management(hexagons, r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_Story_061719.gdb\NV_Hexagons")
arcpy.CopyFeatures_management(hydrobasins, r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_Story_061719.gdb\NV_HydrographicAreas")

# Remove unnecessary fields from hydro basin layer
hydrobasin_new = r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_Story_061719.gdb\NV_HydrographicAreas"
drop_fields = ['COUNT_HYD_', 'HA750_2003', 'HA750_2004', 'PLTSYM', 'DES_REAS', 'SCALE', 'DESIG_ORDE', 'PERIMETER']
for field in drop_fields:
    arcpy.DeleteField_management(hydrobasin_new, field)

# END