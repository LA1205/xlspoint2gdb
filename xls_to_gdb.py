# This script aims to convert the .csv coordinate forest compartment table to a feature class in gdb
import arcpy

# Set the gdb directory and name
work_folder_path = "C:\\output" # <<<<<<replace with your own work path
out_gdbName = "myNewGDB.gdb" # <<<<<<replace with your own name
arcpy.CreateFileGDB_management(work_folder_path, out_gdbName)

# Import the .csv coordinate forest compartment table to your gdb
arcpy.env.workspace = work_folder_path
# Choose your .csv tables below, they should be stored in work foler path
tables = arcpy.ListTables(
    [
        "table_1.csv" # <<<<<<replace with your own compartment table name
    ]
)
outLocation = work_folder_path + "\\" + out_gdbName
print("Importing tables to gdb: " + outLocation)
arcpy.TableToGeodatabase_conversion(tables, outLocation)

# Gnerate a feature class from x and y coordinate in table
arcpy.env.workspace = outLocation
gdb_tableName = str(tables[0])[:-4] # obtain the name of table
in_table = outLocation + "\\" + gdb_tableName
out_feature_class = "myNewpoint" # <<<<<<replace with your own feature class name
wkid = 4536 # <<<<<<replace with your target WKID, 4536 as CGCS2000 3 Degree GK CM 81E for example
x_coords = "x"
y_coords = "y"
z_coords = ""
arcpy.management.XYTableToPoint(
    in_table,
    out_feature_class,
    x_coords,
    y_coords,
    z_coords,
    arcpy.SpatialReference(wkid)
)
print("Importing done!")

# Join the feature class with forest compartment
# The qualifiedFieldNames environment is used by Copy Features when persisting 
# the join field names.
"""
arcpy.env.qualifiedFieldNames = False
inFeatures = out_feature_class
joinTable = gdb_tableName
joinField = "OBJECTID"
outFeature = out_feature_class + "_joined"
print("Joining feature class: " + inFeatures +"with table: " + joinTable + "by field: " + joinField)
point_joined_table = arcpy.management.AddJoin(
    inFeatures, 
    joinField, 
    joinTable, 
    joinField
)
# Copy the layer to a new permanent feature class
print("Start copying the joined layer to new permanent feature class...")
arcpy.management.CopyFeatures(
    point_joined_table, 
    outFeature
)
print("The new feature class: " + outFeature + " is saved at: " + outLocation)
"""