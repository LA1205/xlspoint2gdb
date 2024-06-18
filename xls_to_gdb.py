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

# Gnerate a point feature class from x and y coordinate in table
print("Start generating point feature...")
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
print("Point feature: " + out_feature_class + " has been generated!")

# Generate polygon feature class from point feature class
print("Start generating polygon feature from " + out_feature_class + "...")
out_path = outLocation
out_polygon_feature = out_feature_class + "2plygo"
geometry_type = "POLYGON"
template = ""
has_m = "DISABLED"
has_z = "DISABLED"
spatial_ref = arcpy.Describe(outLocation + "\\" + out_feature_class).spatialReference
arcpy.CreateFeatureclass_management(
    out_path, 
    out_polygon_feature, 
    geometry_type,
    template,
    has_m,
    has_z,
    spatial_ref
)
group_field = "groupfield" # <<<<<<set a field for grouping, may need replcaed with your own field name
arcpy.AddField_management(
    out_polygon_feature, 
    group_field, 
    "LONG"
)
# Create a search cursor to obtain point feature 创建一个搜索游标来获取点要素
in_point_feature = out_feature_class
with arcpy.da.SearchCursor(in_point_feature, ["SHAPE@", group_field]) as cursor:
    # Create a dictonary to store the point from each group 创建一个字典来存储每个组的点
    groups = {}
    for row in cursor:
        # obtain the value in group_field
        group_value = row[1]
        # 如果该组还没有在字典中，则在字典中创建一个空列表
        if group_value not in groups:
            groups[group_value] = {"points": [], "field_value": None}
        # 将点添加到该组的列表中
        groups[group_value]["points"].append(row[0].getPart(0))
        # 如果该组的字段值为空，则设置为当前点的字段值
        if groups[group_value]["field_value"] is None:
            groups[group_value]["field_value"] = group_value
# 创建一个插入游标来创建多边形要素
with arcpy.da.InsertCursor(out_polygon_feature, ["SHAPE@", group_field]) as cursor:
    for group in groups.values():
        # 创建一个多边形几何对象
        polygon = arcpy.Polygon(arcpy.Array(group["points"]))
        # 插入新的多边形要素，并设置组字段的值
        cursor.insertRow([polygon, group["field_value"]])
print("Polygon feature: " + out_polygon_feature + " has been generated!")

# Trim the 