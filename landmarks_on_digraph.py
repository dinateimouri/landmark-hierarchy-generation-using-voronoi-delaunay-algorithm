import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def plot_several_levels_of_hierarchical_landmarks_on_digraph(digraph, hierarchical_levels, hierarchical_colors, boundry_shp_file):
    plt.figure(figsize=(80, 80))

    positions = {n_id: [10000000 * digraph.nodes[n_id]['lon'], 10000000 * digraph.nodes[n_id]['lat']] for n_id in digraph.nodes()}
    nodes_color = 'none'
    edges_color = 'k'
    nx.draw_networkx(digraph, positions, node_color=nodes_color, node_size=0, edge_color=edges_color, width=5, arrows=False, with_labels=False)

    for level_idx, levels in enumerate(hierarchical_levels):
        landmarks_csv_file = f'results/Landmarks_hierarchy_level_{levels}.csv'
        landmarks_df = pd.read_csv(landmarks_csv_file)
        landmarks = landmarks_df[['id', 'lon', 'lat']].to_numpy()
        coords = landmarks[:, 1:]
        node_list = landmarks[:, 0].tolist()

        g = nx.DiGraph()
        positions = {i: [10000000 * coords[i][0], 10000000 * coords[i][1]] for i in range(len(coords))}
        g.add_nodes_from(positions.keys())
        nx.draw_networkx(g, positions, node_size=4000, node_color=hierarchical_colors[level_idx], with_labels=False, label=f"Hierarchical Level: {levels}")

    plt.legend(loc=(0.35, 0.91), prop={'size': 90})
    plt.axis('off')
    plt.savefig('results/landmarks_on_digraph_with_legends.png', format="PNG", bbox_inches="tight")
    plt.close()


def add_legend_manually(hierarchical_levels, hierarchical_colors):
    legend_elements = []
    for i, level in enumerate(hierarchical_levels):
        label = f'Hierarchical Level = {level}'
        element = Line2D([0], [0], marker='o', color='w', label=label,
                         markerfacecolor=hierarchical_colors[i], markersize=15)
        legend_elements.append(element)

    fig, ax = plt.subplots()
    ax.legend(handles=legend_elements, loc='center')
    plt.savefig('results/legends.png', format="PNG")
    plt.close()
