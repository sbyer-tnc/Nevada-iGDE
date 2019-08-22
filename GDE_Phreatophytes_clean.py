#-------------------------------------------------------------------------------
# Name:        NV iGDE Database - Phreatophytes
# Purpose:     Aggregate multiple data sources into a single phreatophyte polygon layer for the NV iGDE database
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
# Process vegetation rasters from TNC

# Read in rasters from the workspace
raster_path = r"K:\GIS3\Projects\GDE\Geospatial\Geodatabase_Layers\GDE_Vegetation\TNCData\ReclassedRasters"
env.workspace = raster_path
rlist = arcpy.ListRasters("", "tif") # list raster file names in the workspace
rlist_sub = rlist[0:3] + rlist[4:8] + rlist[9:] # Remove fnlTJR_sysxcla_1pt5_compr.tif and SpringValleySysxCla_052318.tif from the list

m = list(map(arcpy.Raster, rlist_sub)) # read files in as rasters
type(m[0]) # confirm that m contains a list of Rasters
len(m) # number of rasters in the list

# List source codes for each raster:
tncSourceCodes = ['nvtnc1', 'nvtnc2', 'nvtnc3', 'nvtnc4', 'nvtnc5', 'nvtnc6', 'nvtnc7', 'nvtnc8', 'nvtnc9', 'nvtnc10', 'nvtnc11']

# Get field names for all raster:
for r in m:
    print(r)
    print([f.name for f in arcpy.ListFields(r)])
    # 'BSYSCODE', 'BSYS_CODE' and 'SYS_NAME' are the options for getting ONLY the vegetation code

#-------------------------------------------------------------------------------

# Convert all rasters to polygons to keep native resolution:
env.workspace = path

# Convert raster to polygon, store the SYS CODE field which describes the reference biophysical setting (vegetation) 
# Assigns source code from tncSourceCodes (above)
# """NOTE: large, fine-resolution rasters may not process using Python. Change the range below to process one or a few rasters at a time.
for raster in range(0, 1): # Change range - run for a couple rasters at a time
    outname = gdb_path + r"/" + str(m[raster])[:-4] + "_poly" # Output fc name
    print("Processing " + str(m[raster]) + "...")
    rastername = raster_path + r"/" + str(m[raster])
    rasterFields = [f.name for f in arcpy.ListFields(rastername)]
    
    if 'SYS_CODE' in rasterFields: # Rasters have different field name for the veg code
        print("Converting raster to polygon and storing the SYS_CODE field.")
        rpoly = arcpy.RasterToPolygon_conversion(rastername, outname, "NO_SIMPLIFY", "SYS_CODE")
    
    elif 'BSYS_CODE' in rasterFields:
        print("Converting raster to polygon and storing the BSYS_CODE field.")
        rpoly = arcpy.RasterToPolygon_conversion(rastername, outname, "NO_SIMPLIFY", "BSYS_CODE")
    
    else:
        print("Converting raster to polygon and storing the BSYSCODE field.")
        rpoly = arcpy.RasterToPolygon_conversion(rastername, outname, "NO_SIMPLIFY", "BSYSCODE")

    # Add source code to polygone feature class
    arcpy.AddField_management(rpoly, 'SOURCECODE', 'TEXT', field_length = 20)
    arcpy.CalculateField_management(rpoly, "SOURCECODE", "'{}'".format(tncSourceCodes[raster]), "PYTHON_9.3")
    print("Souce Code " + str(tncSourceCodes[raster]) + " added to SOURCECODE field.")

# Get list of polygon fcs
tncpoly = arcpy.ListFeatureClasses("*_poly")
tncpoly = sorted(tncpoly, key=str.lower)
len(tncpoly)  

#-------------------------------------------------------------------------------
    
# Create polygon boundaries for each mapped area

# Create a list of raster data resolutions for each mapped area
resolutions = []
for i in range(0,len(m)): # get cell size from all rasters in the list
    print(str(m[i]) + " " + str(m[i].meanCellHeight))
    res = round(m[i].meanCellHeight, 1)
    resolutions.append(res)
print(resolutions)


# Dissolve first polygon fc to create a template fc to store the remaining fc boundaries
poly1 = tncpoly[0]
tnc_polygon_bnd = arcpy.Dissolve_management(poly1, path + "\\tnc_project_area_polygons")
arcpy.AddField_management(tnc_polygon_bnd, "RES_METERS", "FLOAT") # Add field that stores the resolution in meters
poly1_res = resolutions[0]
arcpy.CalculateField_management(tnc_polygon_bnd, "RES_METERS", poly1_res)
arcpy.AddField_management(tnc_polygon_bnd, "FILENAME", "TEXT") # Add field that stores the file name
poly1_name = str(m[0])
arcpy.CalculateField_management(tnc_polygon_bnd, "FILENAME", '"' + poly1_name + '"') 
arcpy.AddField_management(tnc_polygon_bnd, "SOURCECODE", "TEXT") # Add field that stores the source code
poly1_code = str(tncSourceCodes[0])
arcpy.CalculateField_management(tnc_polygon_bnd, "SOURCECODE", '"' + poly1_code + '"') 
[f.name for f in arcpy.ListFields(tnc_polygon_bnd)]


# Dissolve the remaining areas and append to the first polygon feature
for poly in range(1, len(tncpoly)):
    area = tncpoly[poly]
    outname = path + "\\temp_boundary"
    
    # Dissolve the polygon fc to create a single polygon feature for the mapped area
    print("Dissolving " + str(area) + "...")
    area_boundary = arcpy.Dissolve_management(area, outname)
    
    # Add resolution information from raster
    arcpy.AddField_management(area_boundary, "RES_METERS", "FLOAT")
    area_resolution = resolutions[poly]
    print("Designating area native resolution at " + str(area_resolution) + " meters...")
    arcpy.CalculateField_management(area_boundary, "RES_METERS", area_resolution)
    
    # Add fields that store the file name and source code
    arcpy.AddField_management(area_boundary, "FILENAME", "TEXT")
    area_name = str(m[poly])
    arcpy.CalculateField_management(area_boundary, "FILENAME", '"' + area_name + '"') 
    arcpy.AddField_management(area_boundary, "SOURCECODE", "TEXT")
    area_code = str(tncSourceCodes[poly])
    arcpy.CalculateField_management(area_boundary, "SOURCECODE", '"' + area_code + '"')
    
    # Append boundary to template fc created above
    arcpy.Append_management(area_boundary, tnc_polygon_bnd, "NO_TEST")

# Save copy of the boundary fc
arcpy.CopyFeatures_management(tnc_polygon_bnd, path + "\\TNC_MappedAreas")

# Clip boundaries to to extent of Nevada
nv = r"K:\GIS3\States\NV\Nevada_83.shp"
tnc_polygon_bnd = path + "\\tnc_project_area_polygons"
arcpy.Clip_analysis(tnc_polygon_bnd, nv, path + "\\TNC_MappedAreas_NV")

# Calculate acres of each mapped area
tnc_areas = path + "\\TNC_MappedAreas_NV"
arcpy.AddField_management(tnc_areas, "Acres", "DOUBLE")
arcpy.CalculateGeometryAttributes_management(tnc_areas, [["Acres", "AREA"]], "", "ACRES", env.outputCoordinateSystem)

# TNC Mapped Areas polygon will be used to mask DRI and Landfire phreatophyte data
# If TNC did not map GDEs in their study areas, then there are not GDEs there


#-------------------------------------------------------------------------------
# Erase portion of Wassuk Range overlapped by Mt Grant

# Isolate Mt Grant boundary
grant = arcpy.Copy_management(tnc_areas, "mtgrant_bnd")
with arcpy.da.UpdateCursor(grant, ['FILENAME']) as cursor:
    for row in cursor:
        if row[0] != "MtGrant_MaskSYSxCLA052918.tif":
            cursor.deleteRow()
del cursor
arcpy.GetCount_management(grant)

# Erase wassuk features using mt grant mask. Creates a donut in the Wassuk Range vegetation fc
wassuk = tncpoly[10]
wassuk_erase = arcpy.Erase_analysis(wassuk, grant, "wassuk_erase")

# Replace existing wassuk polygon feature with new, erased feature
arcpy.Delete_management(tncpoly[10])
arcpy.Copy_management(wassuk_erase, "Wassuk_MaskSYSxCLA052918__poly")


#-------------------------------------------------------------------------------
# Prep polygons to retain wetland and non-wetland GDEs from the BpS codes

# Read in lookup table with codes and names for identified GDE systems (includes phreatophytes and wetlands)
gde_code_csv = r"K:\GIS3\Projects\GDE\Tables\TNC_Raster_GDE_Systems.csv"
gde_code_tbl = arcpy.TableToTable_conversion(gde_code_csv, path, "TNC_GDE_Codes")
gde_codes = list()
with arcpy.da.SearchCursor(gde_code_tbl, ['SYS_CODE']) as cursor:
    for row in cursor:
        code = row[0]
        print(code)
        gde_codes.append(code)
del cursor
print(gde_codes)

# """NOTE code 11542 in IL ranch is "Owyhee River Riparian" was not included. It would be Wetland.
# General polygons i nthe Wetland dataset do include the riparian around the Owyhee River


# Fix erroneous system codes that will be GDEs
# Spring Mountains - update Mesquite code
sm = tncpoly[6]
with arcpy.da.UpdateCursor(sm, ['gridcode']) as cursor:
    for row in cursor:
        if row[0] == 11550:
            row[0] = 11551
            cursor.updateRow(row)
del cursor

# Great Basin NP - update Ponderosa Pine Riparian code
gb = tncpoly[3]
with arcpy.da.UpdateCursor(gb, ['gridcode']) as cursor:
    for row in cursor:
        if row[0] == 11550:
            row[0] = 10542
            cursor.updateRow(row)
del cursor

#-------------------------------------------------------------------------------
# Retain only GDEs from vegetation feature classes

# Dissolve vegetation fcs by BpS code and source code
for feat in range(0, len(tncpoly)):
    poly = tncpoly[feat]
    poly_name = str(poly)[:-5] + "_dissolve"
    print("Dissolving " + str(poly) + "...")
    poly_dissolve = arcpy.Dissolve_management(poly, poly_name, ["GRIDCODE", "SOURCECODE"])

# Delete polygons that are NOT GDEs according to the gde_codes list
tncpoly_dissolved = sorted(arcpy.ListFeatureClasses("*_dissolve*"), key=str.lower)
print(tncpoly_dissolved)  
for feat in range(0, len(tncpoly_dissolved)):
    poly = tncpoly_dissolved[feat]
    print("Deleting non-GDE polygons from " + str(poly) + "...")
    with arcpy.da.UpdateCursor(poly, ['GRIDCODE']) as cursor:
        for row in cursor:
            if not(row[0] in gde_codes):
                cursor.deleteRow()
    del cursor

# Combine all polygon datasets
# Copy first polygon fc and append remaining fcs
processed_polygons = arcpy.ListFeatureClasses("*_dissolve")
print(processed_polygons)
combine_tnc = arcpy.CopyFeatures_management(processed_polygons[0], path + "\\TNC_AllGDE")
arcpy.Append_management(processed_polygons[1:], combine_tnc, "NO_TEST")
[f.name for f in arcpy.ListFields(combine_tnc)]

# Join BpS name (SYS_NAME) using GDE code table
gde_code_tbl = path + "\\TNC_GDE_Codes"
arcpy.JoinField_management(combine_tnc, "GRIDCODE", gde_code_tbl, "SYS_CODE", ["SYS_CODE", "SYS_NAME"])

# Clip TNC GDE polygon fc to extent of Nevada
nv = r"K:\GIS3\States\NV\Nevada_83.shp"
tnc_veg = path + "\\TNC_AllGDE"
tnc_veg_clip = arcpy.Clip_analysis(tnc_veg, nv, "TNC_AllGDE_NV")

#-------------------------------------------------------------------------------
# Separate features that are wetlands or phreatophytes
# Wetland polygons will be sent to Ken McGwire at DRI to use in the EPA Wetlands layer

# Use Wetland attribute in gde_code_tbl to identify wetland-type polygons
arcpy.JoinField_management(tnc_veg_clip, "SYS_CODE", gde_code_tbl, "SYS_CODE", ["Wetland"])

# Make a copy of the phreatophytes polygon - this will have only wetland-types that go to Ken
wetland_poly = arcpy.Copy_management(tnc_veg_clip, "tnc_wetland_phreatophytes")

# Remove wetland polygons from the phreatophyte layer
with arcpy.da.UpdateCursor(tnc_veg_clip, ['Wetland']) as cursor:
    for row in cursor:
        if row[0] != "No":
            cursor.deleteRow()
del cursor

# Remove Wetland attribute
arcpy.DeleteField_management(tnc_veg_clip, ['Wetland'])

# Remove phreatophyte polygons from the wetland layer for Ken
with arcpy.da.UpdateCursor(wetland_poly, ['Wetland']) as cursor:
    for row in cursor:
        if row[0] == "No":
            cursor.deleteRow()
del cursor

# Save the wetland fc that will be sent to Ken
arcpy.CopyFeatures_management(wetland_poly, r"K:\GIS3\Projects\GDE\Geospatial\Geodatabase_Layers\GDE_Wetlands\TNC_Wetland_Phre_050919.shp")

#-------------------------------------------------------------------------------
# Add the new TNC polygon features to the Phreatophyte layer in the iGDE Database with field mapping.

gde_gdb = r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_050919.gdb"
env.workspace = gde_gdb
arcpy.ListFeatureClasses()
path = env.workspace

# Create custom function for field mapping
def mapFields(inlayer, infield, mapfield_name, mapfield_alias, mapfield_type): # mapFields function
    fldMap = arcpy.FieldMap()
    fldMap.addInputField(inlayer, infield)
    mapOut = fldMap.outputField
    mapOut.name, mapOut.alias, mapOut.type = mapfield_name, mapfield_alias, mapfield_type
    fldMap.outputField = mapOut
    return fldMap

# Load Phreatophyte layer from template
gde_phr = gde_gdb + "\\Phreatophytes"

# Load TNC GDE data
tnc_veg = path + "\\TNC_AllGDE_NV"

# Add Phreatophyte Group to the attribute table of TNC layer (generalizes phreatophyte types in the public database)
phrea_lut = r"K:\GIS3\Projects\GDE\Tables\GDE_Phreatophyte_NameCodeGroup.csv"
phrea_tbl = arcpy.TableToTable_conversion(phrea_lut, path, "gde_phreatophyte_lut")
arcpy.JoinField_management(tnc_veg, "SYS_CODE", phrea_tbl, "SYS_CODE", ["SYS_GROUP"])

# Append TNC Phreatophytes to GDE Phreatophytes layer
veg_type_map = mapFields(tnc_veg, "SYS_NAME", "PHR_TYPE", "Phreatophyte Type", "TEXT")
veg_group_map = mapFields(tnc_veg, "SYS_GROUP", "PHR_GROUP", "Phreatophyte Group", "TEXT")
source_map = mapFields(tnc_veg, "SOURCECODE", "SOURCE_CODE", "Source Code", "TEXT")
fldMap_list = [veg_type_map, veg_group_map, source_map]
allFldMappings = arcpy.FieldMappings()
for fm in fldMap_list:
    allFldMappings.addFieldMap(fm)
arcpy.Append_management(tnc_veg, gde_phr, "NO_TEST", allFldMappings)


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Process phreaotphytes from Landfire BpS

gde_phr = r"K:\GIS3\Projects\GDE\Geospatial\NV_iGDE_050919.gdb\Phreatophytes"
env.workspace = path
# Load LANDFIRE BpS
lf_bps = r"K:\GIS3\States\NV\Landfire_BPS_NV\US_140BPS_20180618\grid\us_140bps"

# Read in lookup table with codes and names for identified non-wetland GDE systems in Landfire
lf_code_csv = r"K:\GIS3\Projects\GDE\Tables\Landfire_TNC_GDE_lut.csv"
lf_code_tbl = arcpy.TableToTable_conversion(lf_code_csv, path, "LF_GDE_Codes")
lf_codes = list()
with arcpy.da.SearchCursor(lf_code_tbl, ['SYS_CODE']) as cursor:
    for row in cursor:
        code = row[0]
        lf_codes.append(code)
del cursor
print(lf_codes)

# Subset out the non-wetland GDE classes
lf_copy = arcpy.Copy_management(lf_bps, "LF_BPS_Copy")
with arcpy.da.UpdateCursor(lf_copy, ['BPS_CODE']) as cursor:
    for row in cursor:
        if row[0] not in lf_codes:
            cursor.deleteRow()
del cursor

# Remove the non-Nevada mesquite - These are warm desert riparian systems that are NOT in Nevada zone 13 (1311551)
# """NOTE Keep an eye on this process"""
bad_mesquite = [1411551, 1511551]
with arcpy.da.UpdateCursor(lf_copy, ['BPS_MODEL']) as cursor:
    for row in cursor:
        if row[0] in bad_mesquite:
            print("Deleting bad mesquite")
            cursor.deleteRow()
del cursor

# Convert lf from raster to polygon
arcpy.RasterToPolygon_conversion(lf_copy, "Landfire_GDE_Subset", "NO_SIMPLIFY", "BPS_CODE")
lf_poly = path + "\\Landfire_GDE_Subset"

# Clip to Nevada
nv = r"K:\GIS3\States\NV\Nevada_83.shp"
lf_clip = arcpy.Clip_analysis(lf_poly, nv, "LF_GDE_NV")

# Erase section overlapped by TNC data - TNC data take priority
tnc_cover = path + "\\TNC_MappedAreas_NV"
lf_poly_erase = path + '\\Landfire_GDE_Erase'
arcpy.Erase_analysis(lf_clip, tnc_cover, lf_poly_erase)

# Dissolve polygons in lf by BpS and join SYS_GROUPs and SYS_CODEs from the lookup table
lf_veg = arcpy.Dissolve_management(lf_poly_erase, path + "\\LF_GDE_Dissolve", ["gridcode"])
arcpy.JoinField_management(lf_veg, "gridcode", phrea_tbl, "SYS_CODE", ["SYS_GROUP", "SYS_CODE", "SYS_NAME"])

#-------------------------------------------------------------------------------
# Limit greasewood coverage from LANDFIRE to DRI goundwater discharge boundaries

# Make a copy of the lf fc to process greasewood features
lf_greasewood = arcpy.Copy_management(lf_veg, "lf_greasewood")

# Keep only greasewood in Greasewood layer
with arcpy.da.UpdateCursor(lf_greasewood, ['SYS_CODE']) as cursor:
    for row in cursor:
        if row[0] != 11530:
            print ("Deleting non-greasewood from Greasewood layer...")
            cursor.deleteRow()
del cursor

# Isolate Phreatophyte-type boundaries from basin dataset
gw_basins = r"K:\GIS3\Projects\GDE\Geospatial\Geodatabase_Layers\GDE_Vegetation\NV_ETunit_2019_package_updates\NV_ETunit_2019.shp"
basins = arcpy.CopyFeatures_management(gw_basins, "basin_phreatophytes")
phreatophyte_options = ["Phreatophyte", "Phreatophytes"]

with arcpy.da.UpdateCursor(basins, ['Type']) as cursor:
    for row in cursor:
        if row[0] not in phreatophyte_options:
            cursor.deleteRow()
del cursor

# Clip lf greasewood features to discharge boundaries
lf_greasewood_basins = arcpy.Clip_analysis(lf_greasewood, basins, "lf_greasewood_basins")

# Remove unedited greasewood from original landfire phreatophyte layer
with arcpy.da.UpdateCursor(lf_veg, ['SYS_CODE']) as cursor:
    for row in cursor:
        if row[0] == 11530:
            print ("Deleting Greasewood...")
            cursor.deleteRow()
del cursor

# Add edited Greasewood back into landfire phreatophyte layer
lf_phr = arcpy.Copy_management(lf_veg, "LF_PHR_Fixed")
arcpy.Append_management(lf_greasewood_basins, lf_phr, "NO_TEST")

# Add source code field to lf fc
arcpy.AddField_management(lf_phr, "SOURCECODE", "TEXT")
with arcpy.da.UpdateCursor(lf_phr, "SOURCECODE") as cursor:
    for row in cursor:
        row[0] = "lf"
        cursor.updateRow(row)
        print("Source Code updated to lf")
del cursor
arcpy.GetCount_management(lf_phr)

#-------------------------------------------------------------------------------

# Append landfire to GDE Phreatophytes layer; fill in fields
lf_name_map = mapFields(lf_phr, "SYS_NAME", "PHR_TYPE", "Phreatophyte Type", "TEXT")
lf_code_map = mapFields(lf_phr, "SYS_CODE", "PHR_CODE", "Phreatophyte Code", "LONG")
lf_group_map = mapFields(lf_phr, "SYS_GROUP", "PHR_GROUP", "Phreatophyte Group", "TEXT")
lf_source_map = mapFields(lf_phr, "SOURCECODE", "SOURCE_CODE", "Source Code", "TEXT")
fldMap_list = [lf_name_map, lf_code_map, lf_group_map, lf_source_map]
lfFldMappings = arcpy.FieldMappings()
for fm in fldMap_list:
    lfFldMappings.addFieldMap(fm)
arcpy.Append_management(lf_phr, gde_phr, "NO_TEST", lfFldMappings) # Append Landfire GDE features to Vegetation layer

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Process groundwater discharge boundary data from DRI 

# Load layers used to mask (take priority over) DRI boundaries
tnc_cover = path + "\\TNC_MappedAreas_NV"
landfire_cover = path + "\\LF_PHR_Fixed"

# Path to all hydrographic basins provided in May 2019
gw_basins = r"K:\GIS3\Projects\GDE\Geospatial\Geodatabase_Layers\GDE_Vegetation\NV_ETunit_2019_package_updates\NV_ETunit_2019.shp"

# Make a copy of the boundaries and delete non-phreatphyte features
basins = arcpy.CopyFeatures_management(gw_basins, "basin_phreatophytes")
with arcpy.da.UpdateCursor(basins, ['Type']) as cursor:
    for row in cursor:
        if "Phreatophyte" not in str(row[0]):
            print(row[0])
            cursor.deleteRow()
del cursor

# Clip to extent of Nevada
nv = r"K:\GIS3\States\NV\Nevada_83.shp"
basins_clip = arcpy.Clip_analysis(basins, nv)

# Assign source code to features
# Desert Research Institute Phreatophytes = "drip"
arcpy.AddField_management(basins_clip, "SOURCE_CODE", "TEXT")
with arcpy.da.UpdateCursor(basins_clip, ["SOURCE_CODE"]) as cursor:
    for row in cursor:
        row[0] = "drip"
        cursor.updateRow(row)
del cursor

# Add phreatopgyte fields
arcpy.AddField_management(basins_clip, "PHR_GROUP", "TEXT")
arcpy.AddField_management(basins_clip, "PHR_TYPE", "TEXT")
[f.name for f in arcpy.ListFields(basins_clip)]

# Dissolve basin phreatophyte layer
basins_dissolve = arcpy.Dissolve_management(basins_clip, "basins_dissolve", ["HYD_AREA", "HYD_AREA_N", "PHR_GROUP", "PHR_TYPE", "SOURCE_CODE"])

# Mask with overlapping TNC data
basins_erase1 = arcpy.Erase_analysis(basins_dissolve, tnc_cover, "basins_erase1")

# Mask with overlapping Landfire data
basins_erase2 = arcpy.Erase_analysis(basins_erase1, landfire_cover, "basins_erase2")

# Assign to all boundaries "Unknown Phreatophytes" and "Unknown" to PHR_TYPE and PHR_GROUP, respectively
with arcpy.da.UpdateCursor(basins_erase2, ['PHR_TYPE', 'PHR_GROUP']) as cursor:
    for row in cursor:
        row[0] = "Unknown Phreatophytes"
        row[1] = "Unknown"
        cursor.updateRow(row)
del cursor

# Append basin phreatophyte features to GDE phreaotphytes layer
type_map = mapFields(basins_erase2, "PHR_TYPE", "PHR_TYPE", "Phreatophyte Type", "TEXT")
group_map = mapFields(basins_erase2, "PHR_GROUP", "PHR_GROUP", "Phreatophyte Group", "TEXT")
source_map = mapFields(basins_erase2, "SOURCE_CODE", "SOURCE_CODE", "Source Code", "TEXT")
comment_map = mapFields(basins_erase2, "HYD_AREA_N", "COMMENTS", "Comments", "TEXT")
fldMap_list = [type_map, group_map, source_map, comment_map]
allFldMappings = arcpy.FieldMappings()
for fm in fldMap_list:
    allFldMappings.addFieldMap(fm)
arcpy.Append_management(basins_erase2, gde_phr, "NO_TEST", allFldMappings)

# END