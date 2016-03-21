# USAGE
# python color_kmeans.py --image images/jp.png --clusters 3

from sklearn.cluster import KMeans
import argparse
import utils
import cv2
import numpy as np


def colorCluster(img, k, v_threshold):
    # load the image and convert it from BGR to RGB so that
    # we can dispaly it with matplotlib
    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # reshape the image to be a list of pixels
    image = image.reshape((image.shape[0] * image.shape[1], 3))

    # cluster the pixel intensities
    clt = KMeans(n_clusters=k)
    clt.fit(image)

    hist = utils.centroid_histogram(clt)
    zipped = zip(hist, clt.cluster_centers_)

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

        luma = 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]

        # using luma values to find white and black

        if luma < 20:
            hasblack = color

    if max_var_color is not None and max_var != 0:
        return max_var_color

    return hasblack
