import csv
from digraph import create_osm_digraph
from create_voronoi import create_plot_voronoi
from create_voronoi_with_delaunay import create_plot_voronoi_with_delaunay
from create_landmark_hierarchy import hierarchy
from landmarks_on_digraph import plot_several_levels_of_hierarchical_landmarks_on_digraph


# OSM digraph creation
csv_file_name = 'extracted_hamburg_landmarks.csv'
csv_columns = ['DP_ID', 'Landmark_Lon', 'Landmark_Lat', 'Landmark_Type', 'DP_Landmark_Distance', 'Landmark_Weight']
osm = 'extracted_hamburg.osm'

with open(csv_file_name, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()

digraph = create_osm_digraph(osm, csv_file_name)
# create_digraph.plot_graph(digraph, 'results\extracted_hamburg_digraph.png')


# Boundary shape file: open QGIS, vector/quick osm/quick osm/osm file/osm file location/open, layer/save as/file name/save
boundary_shp_file = 'hamburg_without_holes.shp'
landmarks_csv_file = 'extracted_hamburg_landmarks_with_weight.csv'


# Voronoi creation
# create_plot_voronoi(boundary_shp_file, landmarks_csv_file)


# Voronoi with Delaunay creation
# hierarchy_level = 0
# create_plot_voronoi_with_delaunay(boundary_shp_file, landmarks_csv_file, hierarchy_level)


# Landmark hierarchy
# hierarchy(boundary_shp_file, landmarks_csv_file)


# Plot several levels of hierarchy on the digraph
hierarchical_levels = [10, 15, 20, 25]
hierarchical_colors = ['k', 'm', 'c', 'orange']
plot_several_levels_of_hierarchical_landmarks_on_digraph(digraph, hierarchical_levels, hierarchical_colors, boundary_shp_file)
