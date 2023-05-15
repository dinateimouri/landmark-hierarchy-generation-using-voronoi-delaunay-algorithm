import csv
from create_voronoi_with_delaunay import create_plot_voronoi_with_delaunay


def hierarchy(boundary_shp_file, landmarks_csv_file):
    level = 0

    with open(landmarks_csv_file) as file:
        reader = csv.reader(file)
        num_of_landmarks = len(list(reader)) - 1

    while num_of_landmarks > 1:
        print(f'number of landmarks is: {num_of_landmarks}')
        print(f'level is : {level}')
        landmarks_csv_file = create_plot_voronoi_with_delaunay(boundary_shp_file, landmarks_csv_file, level)
        if not landmarks_csv_file:
            return False

        with open(landmarks_csv_file) as file:
            reader = csv.reader(file)
            num_of_landmarks = len(list(reader)) - 1
        level += 1

    return
