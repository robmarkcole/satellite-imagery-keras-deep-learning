import keras as k
import numpy as np

from utils.augmentation import *

# Reference: https://gist.github.com/baraldilorenzo/07d7802847aaad0a35d3
# BGR mean values [103.94, 116.78, 123.68] should be subtracted before feeding into VGG and ResNet models
def subtract_mean(im):
	im[:,:,:,0] -= 103.939
	im[:,:,:,1] -= 116.779
	im[:,:,:,2] -= 123.68

class BottleNeckImgGenerator(object):
	""" Generate images in batches.  
	Perform image augmentations (e.g. flip horizon) 
	Perform int8 to float16, subtract mean, transpose
	Generators will loop indefinitely as required by Keras fit_generator """
	
	def bottleNeckGen(self, x_train, batch_size):
		"""
		BUG with using H5PYMatrix: x_train can be a H5PYMatrix which doesn't support wrap index like numpy arrays
  		File "<ipython-input-18-e0327f6f3a82>", line 18, in bottleNeckGen
    	x_result = x_train[i: i + batch_size]
  		File "C:\Users\Me\Anaconda2\lib\site-packages\keras\keras\utils\io_utils.py", line 74, in __getitem__
    	raise IndexError
		"""
		i = 0
		limit = x_train.shape[0]
		while True:
			if i+1 >= limit:
				i = 0
			if i + batch_size > limit:
				end = limit
			else:
				end = i + batch_size

			# int8 to float16, subtract mean, transpose
			x_result = x_train[i: i + batch_size].astype(np.float16)
			subtract_mean(x_result)
			x_result = x_result.transpose(0,3,1,2) # theano expects channels come before dims

			i += batch_size
			yield x_result

	# with image augmentation
	def trainGen(self, x_train, y_train, batch_size):
		"""
		BUG with using H5PYMatrix: x_train can be a H5PYMatrix which doesn't support wrap index like numpy arrays
  		File "<ipython-input-18-e0327f6f3a82>", line 18, in bottleNeckGen
    	x_result = x_train[i: i + batch_size]
  		File "C:\Users\Me\Anaconda2\lib\site-packages\keras\keras\utils\io_utils.py", line 74, in __getitem__
    	raise IndexError
		"""
		i = 0
		limit = x_train.shape[0]
		while True:
			if i+1 >= limit:
				i = 0
			if i + batch_size > limit:
				end = limit
			else:
				end = i + batch_size

			# int8 to float16, subtract mean, transpose
			x_result = x_train[i: i + batch_size].astype(np.float16)
			x_result = apply_augment_sequence(x_result)
			subtract_mean(x_result)
			x_result = x_result.transpose(0,3,1,2) # theano expects channels come before dims

			yield x_result, y_train[i: i + batch_size]
			i += batch_size

	def validationGen(self, x_valid, y_valid, batch_size):
		"""
		BUG with using H5PYMatrix: x_valid can be a H5PYMatrix which doesn't support wrap index like numpy arrays
  		File "<ipython-input-18-e0327f6f3a82>", line 18, in bottleNeckGen
    	x_result = x_valid[i: i + batch_size]
  		File "C:\Users\Me\Anaconda2\lib\site-packages\keras\keras\utils\io_utils.py", line 74, in __getitem__
    	raise IndexError
		"""
		i = 0
		limit = x_valid.shape[0]
		while True:
			if i+1 >= limit:
				i = 0
			if i + batch_size > limit:
				end = limit
			else:
				end = i + batch_size

			# int8 to float16, subtract mean, transpose
			x_result = x_valid[i: i + batch_size].astype(np.float16)
			subtract_mean(x_result)
			x_result = x_result.transpose(0,3,1,2) # theano expects channels come before dims

			yield x_result, y_valid[i: i + batch_size]
			i += batch_size

	def testGen(self, x_test, batch_size):
		"""
		BUG with using H5PYMatrix: x_test can be a H5PYMatrix which doesn't support wrap index like numpy arrays
  		File "<ipython-input-18-e0327f6f3a82>", line 18, in bottleNeckGen
    	x_result = x_test[i: i + batch_size]
  		File "C:\Users\Me\Anaconda2\lib\site-packages\keras\keras\utils\io_utils.py", line 74, in __getitem__
    	raise IndexError
		"""
		i = 0
		limit = x_test.shape[0]
		while True:
			if i+1 >= limit:
				i = 0
			if i + batch_size > limit:
				end = limit
			else:
				end = i + batch_size

			# int8 to float16, subtract mean, transpose
			x_result = x_test[i: end].astype(np.float16)
			subtract_mean(x_result)
			x_result = x_result.transpose(0,3,1,2) # theano expects channels come before dims

			yield x_result
			i += batch_size


class CustomImgGenerator(object):
	""" Generate images in batches.  
	Usage: pass to Keras fit_generator. 
	Perform image augmentations (e.g. flip horizon) 
	Generators will loop indefinitely as required by Keras fit_generator """
	def trainGen(self, x_train, y_train, batch_size, scale=True):
		i = 0
		limit = x_train.shape[0]
		#print('limit', limit)
		while True:
			x_result = x_train[i: i + batch_size]
			x_result = x_result.transpose(0,2,3,1) # imgaug expects channels last
			x_result = apply_augment_sequence(x_result)
			if scale:
				x_result = x_result / float(255)
			x_result = x_result.transpose(0,3,1,2)

			#print(x_result.shape)

			yield x_result, y_train[i: i + batch_size]
			if i + 2*batch_size > limit:
				i = 0
			else:
				i += batch_size

	def validationGen(self, x_valid, y_valid, batch_size, scale=True):
		i = 0
		limit = x_valid.shape[0]
		while True:
			yield x_valid[i: i + batch_size] / float(255) if scale else x_valid[i: i + batch_size], y_valid[i: i + batch_size]

			if i + 2*batch_size > limit:
				i = 0
			else:
				i += batch_size

	def testGen(self, x_test, batch_size, scale=True):
		i = 0
		limit = x_test.shape[0]
		while True:
			yield x_test[i: i + batch_size] / float(255) if scale else x_test[i: i + batch_size]
			if i + 2*batch_size > limit:
				i = 0
			else:
				i += batch_size