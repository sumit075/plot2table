from nose.tools import *
import numpy as np

import plottotable
from plottotable import legend_detect

data_dir = plottotable.data_dir

class TestLegendDetect(object):

	def test_getOCRLines(self):
		pass

	def test_getLegendsBox(self):
		pass

	def test_isWord(self):
		pass

	def test_getLegendOrientation(self):
		pass

	def test_parseBlock(self):
		pass

	def test_fetchLegendColors(self):
		out = legend_detect.fetchLegendColors(data_dir + '/legend.ppm')
		assert out['orient'] == 0
		list_str = out['legend'][0][0][16:].split(',')
		assert eval(list_str[0]) == 830
		assert eval(list_str[1]) == 2
		assert eval(list_str[2]) == 987
		assert eval(list_str[3]) == 38

		known_arr = np.array([4.60526316e-02, 2.82960526e+01, 1.35151316e+02])
		assert np.allclose(out['legend'][0][1], known_arr)

	def test_legendLabelCoordinates(self):
		pass
