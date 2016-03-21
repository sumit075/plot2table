from nose.tools import *
import numpy as np

import cv2
import plottotable
from plottotable import axisDetector

data_dir = plottotable.data_dir

class TestAxisDetector(object):

	def setup(self):
		self.img1 = cv2.imread(data_dir + '/garbage.ppm')
		self.img2 = cv2.imread(data_dir + '/legend.ppm')
		self.img3 = cv2.imread(data_dir + '/table.ppm')
		self.img4 = cv2.imread(data_dir + '/title.ppm')

	def test_getPointsOnAxis(self):
		pass

	def test_getPlotLines(self):
		assert not axisDetector.getPlotLines(self.img1)
		assert np.any(axisDetector.getPlotLines(self.img2))
		assert np.any(axisDetector.getPlotLines(self.img3))
		assert np.any(axisDetector.getPlotLines(self.img4))

	def test_AxesDetection(self):
		assert not axisDetector.AxesDetection(self.img2)
		assert not axisDetector.AxesDetection(self.img3)
		assert axisDetector.AxesDetection(self.img4)