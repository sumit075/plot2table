import cv2
from nose.tools import *

import plottotable
from plottotable import garbageImageDetector

data_dir = plottotable.data_dir

class TestGarbageImageDetector(object):

	def test_isAxisPresent(self):
		img = cv2.imread(data_dir + '/table.ppm')
		assert garbageImageDetector.isAxisPresent(img)

	def test_isTable(self):
		img = cv2.imread(data_dir + '/title.ppm')
		assert not garbageImageDetector.isTable(img)

	def test_isGarbageImage(self):
		img = cv2.imread(data_dir + '/title.ppm')
		assert not garbageImageDetector.isGarbageImage(img)
