from nose.tools import *

import plottotable
from plottotable import titleExtractor

data_dir = plottotable.data_dir

class TestTitleExtractor(object):

	def test_getTitle(self):
		title = titleExtractor.getTitle(data_dir + '/title.ppm')
		known_str = '\xe2\x80\x98 u Time Plol'
		# Try analyzing first three characters of title. Magically inserted.
		assert title == known_str
