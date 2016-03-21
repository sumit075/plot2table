from nose.tools import *
import numpy as np

import plottotable
from plottotable import preprocessor

data_dir = plottotable.data_dir

class TestPreprocessor(object):

	def test_resizeImage(self):
		# When rows > col
		img = np.random.rand(600, 400)
		out = preprocessor.resizeImage(img, resizeTo=1000)
		assert out.shape[0] == 1000

		# When rows < col
		img = np.random.rand(400, 600)
		out = preprocessor.resizeImage(img, resizeTo=1000)
		assert out.shape[1] == 1000

		# When rows == col
		img = np.random.rand(400, 400)
		out = preprocessor.resizeImage(img, resizeTo=1000)
		assert out.shape[0] == out.shape[1] == 1000

	def test_morphological(self):
		img = np.load(data_dir + '/test_morphological_in.npy')
		out = preprocessor.morphological(img)
		out_known = np.load(data_dir + '/test_morphological_out.npy')
		assert np.allclose(out, out_known)

	def test_cluster(self):
		img = np.load(data_dir + '/test_cluster_in.npy')
		assert 120 < np.mean(preprocessor.cluster(img)[0]) < 130

	def test_sharpenImage(self):
		img = np.load(data_dir + '/test_sharpenImage_in.npy')
		out = preprocessor.sharpenImage(np.float32(img))
		out_known = np.load(data_dir + '/test_sharpenImage_out.npy')
		assert np.allclose(out, out_known)

	def test_enhance(self):
		img = np.load(data_dir + '/test_enhance_in.npy')
		out = preprocessor.enhance(img)
		out_known = np.load(data_dir + '/test_enhance_out.npy')
		assert np.allclose(out, out_known)

	def test_otsusBinarization(self):
		img = np.load(data_dir + '/test_otsusBinarization_in.npy')
		out = preprocessor.otsusBinarization(np.uint8(img))
		out_known = np.load(data_dir + '/test_otsusBinarization_out.npy')
		assert np.allclose(out, out_known)

	def test_iterativeThresholding(self):
		img = np.load(data_dir + '/test_iterativeThresholding_in.npy')
		out = preprocessor.iterativeThresholding(np.float32(img))
		out_known = np.load(data_dir + '/test_iterativeThresholding_out.npy')
		assert np.allclose(out, out_known)

	def test_makeEnlarged(self):
		pass

	def test_genImages(self):
		pass
