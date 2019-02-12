# -*- coding: utf-8 -*-

import csv
import numpy as np
from PIL import Image
import cv2
import os

def make_dir(input_path):
	try:
		if not(os.path.isdir(input_path)):
			os.makedirs(os.path.join(input_path))
	except OSError as e:
		if e.errno != errno.EEXIST:
			print("Failed to create directory")
			raise


def main():
	labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
	file = np.genfromtxt('fer2013.csv', delimiter=',', dtype=None)

	label_num = np.array([np.fromstring(i, np.uint8, sep=' ') for i in file[1:, :1]])

	images = np.array([np.fromstring(i, np.uint8, sep=' ') for i in file[1:, 1:-1]])

	usage = np.array([i.decode('UTF-8') for i in file[1:,2]])

	# split_data
	cnt = 0
	try:
		while True:
				usage_name = "split_data/" + usage[cnt]
				make_dir(usage_name)

				dirname = usage_name + "/" + labels[label_num[cnt][0]]
				resize_imgae = images[cnt].reshape((48,48))
				make_dir(dirname)
				img_list = os.listdir(dirname)
				# sorting image number
				list.sort(img_list, key=lambda x: int(x.split('.jpg')[0]))
				if len(img_list) < 1:
					cv2.imwrite(dirname + "/1.jpg", resize_imgae)
				else:
					last_img_num = img_list[-1].split('.jpg')[0]
					cv2.imwrite(dirname + "/" + str(int(last_img_num)+1)+'.jpg', resize_imgae)
			cnt += 1
	except:
		print("Finished!!")

if __name__ == '__main__':
	main()
