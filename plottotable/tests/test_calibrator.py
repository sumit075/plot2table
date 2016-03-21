import cv2
from nose.tools import *
import numpy as np

import plottotable
from plottotable import calibrator

data_dir = plottotable.data_dir

class TestCalibrator(object):

	def setup(self):
		self.img1 = cv2.imread(data_dir + '/garbage.ppm')
		self.img2 = cv2.imread(data_dir + '/legend.ppm')
		self.img3 = cv2.imread(data_dir + '/table.ppm')
		self.img4 = cv2.imread(data_dir + '/title.ppm')

	def test_imgResize(self):
		out = calibrator.imgResize(self.img1, 100)
		out_known = np.load(data_dir + '/test_imgResize_in.npy')
		assert np.allclose(out, out_known)

	def test_binarize(self):
		out = calibrator.binarize(self.img1, (1000, 1000))
		out_known = np.load(data_dir + '/test_binarize.npy')
		assert np.allclose(out, out_known)

	def test_getLabelData(self):
		out = calibrator.getLabelData(data_dir + '/title.ppm')
		assert out[0][0] == out[2] == 100.0
		assert out[1] == 1000.0
		assert out[3] < 1
		assert 200 < out[4][0] + out[4][1] < 300
