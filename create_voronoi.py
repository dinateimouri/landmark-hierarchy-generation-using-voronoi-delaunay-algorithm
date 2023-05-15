import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.ops import cascaded_union
from geovoronoi import voronoi_regions_from_coords, points_to_coords
from geovoronoi.plotting import subplot_for_map, plot_voronoi_polys_with_points_in_area


def create_plot_voronoi(boundary_file, landmarks_file):
    crs = 'epsg:4326'

    boundary = gpd.read_file(boundary_file)

    landmarks = pd.read_csv(landmarks_file)
    geometry = [Point(xy) for xy in zip(landmarks['Landmark_Lon'], landmarks['Landmark_Lat'])]
    landmarks_geo = gpd.GeoDataFrame(landmarks, crs=crs, geometry=geometry)

    boundary_shape = cascaded_union(boundary.geometry)
    landmarks_geo = landmarks_geo[landmarks_geo.geometry.within(boundary_shape)]
    coords = points_to_coords(landmarks_geo.geometry)

    poly_shapes, pts, poly_to_pt_assignments = voronoi_regions_from_coords(coords, boundary_shape)

    poly_shapes = [poly for poly in poly_shapes if not isinstance(poly, gpd.GeoSeries)]
    pts = [pts[i] for i, poly in enumerate(poly_shapes)]
    poly_to_pt_assignments = [poly_to_pt_assignments[i] for i, poly in enumerate(poly_shapes)]

    fig, axs = plt.subplots()
    axs.set_aspect('equal', 'datalim')
    boundary_shape.plot(ax=axs, alpha=0.5, facecolor='red')
    plt.savefig('results/cascaded_union_boundary_shape.png')
    plt.show()

    fig, ax = plt.subplots()
    boundary.plot(ax=ax, color='gray')
    landmarks_geo.plot(ax=ax, markersize=20, color='yellow', marker='o', label='landmark')
    ax.legend(prop={'size': 15})
    plt.savefig('results/landmarks_on_boundary_shape.png')
    plt.show()

    fig, ax = subplot_for_map()
    plot_voronoi_polys_with_points_in_area(ax, boundary_shape, poly_shapes, pts, poly_to_pt_assignments)
    ax.set_title('Voronoi regions of landmarks')
    plt.tight_layout()
    plt.savefig('results/plot_voronoi_regions.png')
    plt.show()

    plt.close()
