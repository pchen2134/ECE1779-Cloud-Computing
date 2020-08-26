# import the necessary packages
import numpy as np
import cv2
import os
# load the COCO class labels our YOLO model was trained on
def init_yolo():
	path = os.path.abspath(os.path.dirname(__file__))
	LABELS = open(path + "/yolo-coco/coco.names").read().strip().split("\n")

	# initialize a list of colors to represent each possible class label
	np.random.seed(42)
	COLORS = np.random.randint(0, 255, size=(len(LABELS), 3), dtype="uint8")

	# derive the paths to the YOLO weights and model configuration
	weightsPath = path + "/yolo-coco/yolov3.weights"
	configPath = path + "/yolo-coco/yolov3.cfg"

	# load our YOLO object detector trained on COCO dataset (80 classes)
	print("[INFO] loading YOLO from disk...")
	net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
	return net, LABELS, COLORS
