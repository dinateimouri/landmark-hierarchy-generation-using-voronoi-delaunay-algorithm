from pathlib import Path
import csv
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import cascaded_union
from scipy.spatial import Delaunay
from more_itertools import unique_everseen
from geovoronoi import (
    voronoi_regions_from_coords,
)
from geovoronoi.plotting import plot_voronoi_polys_with_points_in_area
import matplotlib.pyplot as plt

crs = "epsg:4326"


def create_plot_voronoi_with_delaunay(boundary_shp_file, landmarks_csv_file, hierarchy_level):
    csv_columns = [
        "DP_ID",
        "Landmark_Lon",
        "Landmark_Lat",
        "Landmark_Type",
        "DP_Landmark_Distance",
        "Landmark_Weight",
        "Landmark_Geometry",
    ]
    lon_idx, lat_idx, landmark_weight_idx = 1, 2, 5

    boundary = gpd.read_file(boundary_shp_file)
    boundary_shape = cascaded_union(boundary.geometry)

    landmarks_csv_path = Path(landmarks_csv_file)
    with open(landmarks_csv_path, "r") as f:
        landmarks_list_of_lists = list(csv.reader(f))[1:]

    coords = []
    landmarks_temp = []
    for line in landmarks_list_of_lists:
        lon, lat = map(float, line[lon_idx : lat_idx + 1])
        coordinate = [lon, lat]
        p = Point(lon, lat)
        if p.within(boundary_shape):
            landmarks_temp.append(line)
            coords.append(coordinate)

    landmarks = np.array(landmarks_temp)

    print("voronoi regions call")
    poly_shapes, pts, poly_to_pt_assignments = voronoi_regions_from_coords(
        coords, boundary_shape
    )

    indices_to_remove = [
        i for i, poly in enumerate(poly_shapes) if poly.geom_type == "GeometryCollection"
    ]
    for i in reversed(indices_to_remove):
        poly_shapes.pop(i)
        removable_coords_index = poly_to_pt_assignments.pop(i)
        pts = np.delete(pts, removable_coords_index, axis=0)
        coords = np.delete(coords, removable_coords_index, axis=0)
        landmarks = np.delete(landmarks, removable_coords_index, axis=0)

    tri = Delaunay(coords)

    csv_file_with_duplicate = f"results/Landmarks_hierarchy_level_{hierarchy_level}_with_possible_duplicates.csv"
    csv_file = f"results/Landmarks_hierarchy_level_{hierarchy_level}.csv"

    with open(csv_file_with_duplicate, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()

    for i, coord in enumerate(coords):
        i_neighbors_ids = get_neighbor_vertex_ids_from_vertex_id(i, tri)
        i_plus_neighbors_ids = np.append(i_neighbors_ids, i)
        weights = [landmarks[i][landmark_weight_idx] for i in i_plus_neighbors_ids]
        highest_weight_landmark_id = i_plus_neighbors_ids[np.argmax(weights)]
        highest_weight_row = landmarks[highest_weight_landmark_id][:]
        with open(csv_file_with_duplicate, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(highest_weight_row)

    with open(csv_file_with_duplicate, "r", newline="") as in_file, \
            open(csv_file, "w", newline="") as out_file:
        unique_rows = unique_everseen(in_file)
        out_file.writelines(unique_rows)

    plot_name = f"results/plot_voronoi_with_delaunay_hierarchy_level_{hierarchy_level}.png"
    fig, ax = plt.subplots()
    plot_voronoi_polys_with_points_in_area(ax, boundary_shape, poly_shapes, pts, poly_to_pt_assignments)
    coords_array = np.array(coords)
    ax.triplot(coords_array[:, 0], coords_array[:, 1], tri.simplices, lw=0.5)
    ax.plot(coords_array[:, 0], coords_array[:, 1], " ", markersize=0.5)
    fig.savefig(plot_name, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return csv_file


def get_neighbor_vertex_ids_from_vertex_id(vertex_id, triang):
    index_pointers, indices = triang.vertex_neighbor_vertices
    start_index, end_index = index_pointers[vertex_id], index_pointers[vertex_id + 1]
    return indices[start_index:end_index]

