import osmnx as ox
import time
from shapely.geometry import Polygon
import os
import configparser


def save_graph_shapefile_directional(G, filepath=None, encoding="utf-8"):
    # default filepath if none was provided
    if filepath is None:
        filepath = os.path.join(ox.settings.data_folder, "graph_shapefile")

    # if save folder does not already exist, create it (shapefiles
    # get saved as set of files)
    if not filepath == "" and not os.path.exists(filepath):
        os.makedirs(filepath)
    filepath_nodes = os.path.join(filepath, "nodes.shp")
    filepath_edges = os.path.join(filepath, "edges.shp")

    # convert undirected graph to gdfs and stringify non-numeric columns
    gdf_nodes, gdf_edges = ox.utils_graph.graph_to_gdfs(G)
    gdf_nodes = ox.io._stringify_nonnumeric_cols(gdf_nodes)
    gdf_edges = ox.io._stringify_nonnumeric_cols(gdf_edges)
    # We need an unique ID for each edge
    gdf_edges["fid"] = gdf_edges.index
    # save the nodes and edges as separate ESRI shapefiles
    gdf_nodes.to_file(filepath_nodes, encoding=encoding)
    gdf_edges.to_file(filepath_edges, encoding=encoding)


def get_osm(CITY, bounds):
    print("osmnx version", ox.__version__)
    x1, x2, y1, y2 = bounds
    # Enlarge the bounds
    x1 -= 0.03
    x2 += 0.03
    y1 -= 0.03
    y2 += 0.03
    boundary_polygon = Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])
    G = ox.graph_from_polygon(boundary_polygon, network_type='drive')
    # fig, ax = ox.plot_graph(G)
    start_time = time.time()
    save_graph_shapefile_directional(G, filepath='./' + CITY.lower() + '_shp')
    print("--- %s seconds ---" % (time.time() - start_time))


configparser = configparser.RawConfigParser()
configFilePath = r'../config.ini'
configparser.read(configFilePath)

CITY = configparser.get('main-config', "CITY")
bounds = [float(s) for s in configparser.get('main-config', "bb").split(",")]
get_osm(CITY, bounds)
