from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from camera import Camera
import time


import argparse
import io
import time
import numpy as np
import picamera
from databasehelper import Database
import os

from PIL import Image
import tflite_runtime.interpreter as tflite

import motiondetector
def load_labels(filename):
	with open(filename, 'r') as f:
		return [line.strip() for line in f.readlines()]

def sort_trash(imgpath):
	camera = Camera()
	database = Database()

	while True:

		# wait for camera to detect motion, then sleep for a bit to
		# let the object settle down
		print("waiting for motion...")
		motiondetector.waitForMotionDetection(camera.getPiCamera())
		time.sleep(0.5) # Lets object settle down, TODO maybe remove

		print("detected motion")


		# take a photo and classify it
		camera.takePhoto(imgpath)
		#time.sleep(1)
		interpreter = tflite.Interpreter(model_path="mnasmodel.tflite")

		interpreter.allocate_tensors()

		input_details = interpreter.get_input_details()
		output_details = interpreter.get_output_details()

		# check the type of the input tensor
		floating_model = input_details[0]['dtype'] == np.float32

		# NxHxWxC, H:1, W:2
		height = input_details[0]['shape'][1]
		width = input_details[0]['shape'][2]
		img = Image.open("img/classificationImage.jpg").resize((width, height))

		# add N dim
		input_data = np.expand_dims(img, axis=0)

		if floating_model:
			input_data = (np.float32(input_data) - 127.5) / 127.5

		interpreter.set_tensor(input_details[0]['index'], input_data)

		interpreter.invoke()

		output_data = interpreter.get_tensor(output_details[0]['index'])
		results = np.squeeze(output_data)

		top_k = results.argsort()[-5:][::-1]
		labels = load_labels("class_labels.txt")
		for i in top_k:
			if floating_model:
			 	print('{:08.6f}: {}'.format(float(results[i]), labels[i]))
			 	selectedLabel = labels[i]
			else:
			 	print('{:08.6f}: {}'.format(float(results[i] / 255.0), labels[i]))
		
		database.write_result(imgpath, selectedLabel)	
		print("Wrote result to database.")
		time.sleep(1)

def main():
	sort_trash('img/classificationImage.jpg')

if __name__ == '__main__':
	main()
