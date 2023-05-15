import networkx as nx
import xml.sax
import pyproj
from csv import writer
from csv import reader
import pandas as pd
import time
import requests
import csv


class Node:
    def __init__(self, node_id, lon, lat, is_decision_point):
        self.id = node_id
        self.lon = lon
        self.lat = lat
        self.tags = {}
        self.is_decision_point = is_decision_point


class Way:
    def __init__(self, way_id, osm):
        self.osm = osm
        self.id = way_id
        self.nds = []
        self.tags = {}


class OSM:
    def __init__(self, filename_or_stream):
        nodes = {}
        ways = {}

        class OSMHandler(xml.sax.ContentHandler):
            def __init__(self):
                self.curr_elem = None
                self.counter = {}

            def startElement(self, name, attrs):
                if name == 'node':
                    self.curr_elem = Node(attrs['id'], float(attrs['lon']), float(attrs['lat']), False)
                elif name == 'way':
                    self.curr_elem = Way(attrs['id'], self)
                elif name == 'tag':
                    self.curr_elem.tags[attrs['k']] = attrs['v']
                elif name == 'nd':
                    self.curr_elem.nds.append(attrs['ref'])

            def endElement(self, name):
                if name == 'node':
                    nodes[self.curr_elem.id] = self.curr_elem
                elif name == 'way':
                    ways[self.curr_elem.id] = self.curr_elem

            def characters(self, chars):
                pass

            def endDocument(self):
                # Decision Points
                for w in ways.values():
                    if 'highway' in w.tags:
                        highway_types = ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential']
                        if w.tags['highway'] in highway_types:
                            for nd_ref in w.nds:
                                if nd_ref not in self.counter:
                                    self.counter[nd_ref] = 0
                                self.counter[nd_ref] += 1
                intersections_ref = [x for x in self.counter if self.counter[x] > 1]
                print(f'Number of Decision Points : {len(intersections_ref)}')

                for n in nodes.values():
                    if n.id in intersections_ref:
                        n.is_decision_point = True

        xml.sax.parse(filename_or_stream, OSMHandler())
        self.nodes = nodes
        self.ways = ways


def create_osm_digraph(filename: str) -> nx.DiGraph:
    print('Start Digraph Creation ...')

    osm = OSM(filename)
    G = nx.DiGraph()
    for w in osm.ways.values():
        if 'highway' in w.tags:
            if w.tags['highway'] in ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential']:
                w_dp = [n_id for n_id in w.nds if osm.nodes[n_id].isDP]
                if 'oneway' in w.tags and w.tags['oneway'] == 'yes':
                    G.add_path(w_dp, id=w.id)
                else:
                    G.add_path(w_dp, id=w.id)
                    G.add_path(w_dp[::-1], id=w.id)

    print('Node Parameter Calculation ...')

    for DP_id in G.nodes():
        DP = osm.nodes[DP_id]
        neighbor_one = list(G.neighbors(DP_id))
        neighbor_two = list(G.predecessors(DP_id))
        neighbor_list = list(set(neighbor_one) | set(neighbor_two))
        G.nodes[DP_id].update({'lat': DP.lat, 'lon': DP.lon, 'id': DP.id})
        for neighbor_id in neighbor_list:
            node_neighbor = osm.nodes[neighbor_id]
            pointNeighbor = [node_neighbor.lat, node_neighbor.lon]
            pointDP = [G.nodes[DP_id]['lat'], G.nodes[DP_id]['lon']]
            fwd_azimuth_DPNeighbor, back_azimuth_DPNeighbor, distance_DPNeighbor = get_azimuth(pointDP, pointNeighbor)
            if G.has_edge(DP_id, neighbor_id):
                G.edges[DP_id, neighbor_id].update({'bearing': fwd_azimuth_DPNeighbor, 'distance': distance_DPNeighbor})
            else:
                G.edges[neighbor_id, DP_id].update({'bearing': fwd_azimuth_DPNeighbor, 'distance': distance_DPNeighbor})

    print('Edge Parameter Calculation ...')

    for (node1, node2) in G.edges():
        if 'distance' not in G.edges[node1, node2]:
            G.edges[node1, node2]['distance'] = G.edges[node2, node1]['distance']

    return G


def get_azimuth(point_a, point_b):
    lat1, lat2, long1, long2 = point_a[0], point_b[0], point_a[1], point_b[1]
    geodesic = pyproj.Geod(ellps='WGS84')
    fwd_azimuth, back_azimuth, distance = geodesic.inv(long1, lat1, long2, lat2)
    return fwd_azimuth, back_azimuth, distance


def landmark_identification(dp, neighbor_distance_list, csv_file_name):
    landmarks = []
    if neighbor_distance_list:
        around_value = min(50, max(neighbor_distance_list) * 500)  # meters
    else:
        around_value = 50

    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = """
        [out:json];
        (node["amenity"](around:{},{},{}); 
         way["amenity"](around:{},{},{}); 
         rel["amenity"](around:{},{},{}););
        out center;
        """.format(around_value, dp.lat, dp.lon, around_value, dp.lat, dp.lon, around_value, dp.lat, dp.lon)

    headers = {'referer': 'fateme_referer'}
    need_try = True

    while need_try:
        response = requests.get(overpass_url, params={'data': overpass_query}, headers=headers)
        if response.ok:
            need_try = False
            data = response.json()
            for element in data['elements']:
                if element['type'] == 'node':
                    landmark_coords = (element['lat'], element['lon'])
                elif 'center' in element:
                    landmark_coords = (element['center']['lat'], element['center']['lon'])
                else:
                    continue

                fwd_azimuth, back_azimuth, distance = get_azimuth((dp.lat, dp.lon), landmark_coords)
                tags = element['tags']
                landmark_type = tags['amenity']
                landmarks.append({
                    'DP_ID': dp.id,
                    'Landmark_Lon': landmark_coords[1],
                    'Landmark_Lat': landmark_coords[0],
                    'Landmark_Type': landmark_type,
                    'DP_Landmark_Distance': distance
                })

            csv_columns = ['DP_ID', 'Landmark_Lon', 'Landmark_Lat', 'Landmark_Type', 'DP_Landmark_Distance']
            with open(csv_file_name, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writerows(landmarks)
        else:
            need_try = True
            time.sleep(2)


def add_weights_to_landmarks(landmarks_csv_file_without_weight):
    dist_idx = 4
    landmark_type_idx = 3
    dist_weight = 1
    salience_weight = 1

    df = pd.read_csv(landmarks_csv_file_without_weight)
    max_dist = df['DP_Landmark_Distance'].max()
    min_dist = df['DP_Landmark_Distance'].min()
    print(max_dist)
    print(min_dist)

    landmarks_csv_file_with_weight = 'extracted_hamburg_landmarks_with_weight.csv'
    with open(landmarks_csv_file_without_weight, 'r') as read_obj, \
            open(landmarks_csv_file_with_weight, 'w', newline='') as write_obj:
        csv_reader = reader(read_obj)
        csv_writer = writer(write_obj)
        is_header = True

        for row in csv_reader:
            if is_header:
                row.append('Landmark_Weight')
                csv_writer.writerow(row)
                is_header = False

            else:
                salience = calculate_salience(row[landmark_type_idx])
                dist_normalized = (float(row[dist_idx]) - min_dist) / (max_dist - min_dist)
                weight = (dist_weight * (1 - dist_normalized)) + (salience_weight * salience)
                row.append(weight)
                csv_writer.writerow(row)
                print(row)

    return landmarks_csv_file_with_weight


def calculate_salience(landmark_type):
    high_salience = ['university', 'hospital', 'police', 'grave_yard', 'place_of_worship']
    medium_salience = ['bank', 'cinema', 'fire_station', 'bus_station']
    salience = 0
    if landmark_type in high_salience:
        salience = 20
    elif landmark_type in medium_salience:
        salience = 10
    else:
        salience = 1

    return salience



