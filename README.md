# Landmark-Hierarchy-Generation-Using-Voronoi-Delaunay-Algorithm
Geographic features play an essential role in our spatial understanding and navigation. Prominent landmarks, in particular, are critical in providing granular route directions. The prominence of a landmark is determined by its weight, computed using a combination of normalized distance, orientation, and salience of the landmark. In this project, I employ a ranking mechanism to identify the most prominent landmarks in an environment.

To generate a hierarchy of landmarks, I first assign each landmark to its closest decision point, i.e., the intersection nearest to the landmark. The hierarchy of landmarks is generated using the Voronoi-Delaunay algorithm. The algorithm includes the following steps:

A Voronoi partition is generated using all the landmarks as seeds.
A Delaunay triangulation is constructed, which is the dual of the Voronoi partition.
For each triangle, the landmark with the highest weight is chosen for the next level of the hierarchy.
The hierarchy of landmarks is generated only once for each environment and represents the level of salience of a landmark for the global environment. The process results in a hierarchy of landmarks, with higher levels including more prominent landmarks.

For more details on the research behind this code, check out my paper [here] (https://www.sciencedirect.com/science/article/pii/S0198971521001393) and my thesis [here](https://lnkd.in/diu_Y9sp).
