# USAGE
# python color_kmeans.py --image images/jp.png --clusters 3

# import the necessary packages
from sklearn.cluster import KMeans
# import matplotlib.pyplot as plt
import argparse
import utils
import cv2
import numpy as np

# construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required = True, help = "Path to the image")
# ap.add_argument("-c", "--clusters", required = True, type = int,
# 	help = "# of clusters")
# args = vars(ap.parse_args())


def colorCluster(img, k, v_threshold):
	# load the image and convert it from BGR to RGB so that
	# we can dispaly it with matplotlib
	# image = cv2.imread(args["image"])
	image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

	# show our image
	# plt.figure()
	# plt.axis("off")
	# plt.imshow(image)

	# reshape the image to be a list of pixels
	image = image.reshape((image.shape[0] * image.shape[1], 3))

	# cluster the pixel intensities
	clt = KMeans(n_clusters = k)
	clt.fit(image)

	hist = utils.centroid_histogram(clt)
	zipped = zip(hist, clt.cluster_centers_)

	# build a histogram of clusters and then create a figure
	# representing the number of pixels labeled to each color
	# bar = utils.plot_colors(hist, clt.cluster_centers_)

	# show our color chart
	# plt.figure()
	# plt.axis("off")
	# plt.imshow(bar)
	# plt.show()

	# finding the color with max variance > v_threshold, else 
	# return Black if found
	# else return None

	max_var_color = None
	max_var = None
	hasblack = None

	for percent, color in zipped:
		variance = np.var(color)
		if variance < v_threshold:
			variance = 0

		if max_var is None or max_var < variance:
			max_var = variance
			max_var_color = color

		luma = 0.2126 *color[0] + 0.7152 * color[1] + 0.0722 * color[2]

		# using luma values to find white and black

		if luma < 20:
			# print "Black"
			hasblack = color

	if max_var_color is not None and max_var != 0:
		return max_var_color

	return hasblack
