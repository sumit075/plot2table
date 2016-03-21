from nose.tools import *
import numpy as np

import plottotable
from plottotable import color_kmeans

data_dir = plottotable.data_dir

class TestColorKMeans(object):

	def test_colorCluster(self):
		img = np.load(data_dir + '/test_colorCluster_in.npy')
		out = np.mean(color_kmeans.colorCluster(np.float32(img), 5, 100))
		assert 100 < out < 200

