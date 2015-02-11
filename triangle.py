from scipy.spatial import Delaunay

from cities import place_cities

width = 160
height = 90
citycount = 5
distance = 10
cities = place_cities(width, height, citycount, distance)


tri = Delaunay(cities)

print(cities)
print(tri.simplices)
print(tri.points)
print(tri.points[tri.simplices])
