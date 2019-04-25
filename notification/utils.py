from django.conf import settings
import cv2
import numpy as np
import os
from PIL import Image


def _load_model():
    config_path = os.path.join(settings.MODEL_DIR_PATH, settings.MODEL_CONFIG_NAME)
    weight_path = os.path.join(settings.MODEL_DIR_PATH, settings.MODEL_WEIGHT_NAME)
    net = cv2.dnn.readNetFromDarknet(config_path, weight_path)
    layers = net.getLayerNames()
    last_layers = [layers[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return net, last_layers


def _preprocess_image(image):
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0,
                                 settings.MODEL_IMAGE_SIZE,
                                 swapRB=False, crop=False)
    return blob


def count_bottles(image):
    full_cnt = 0
    empty_cnt = 0
    if settings.CACHED_MODEL is None:
        settings.CACHED_MODEL, settings.LAST_LAYER_NAMES = _load_model()
    h, w = image.shape[:2]
    blob = _preprocess_image(image)
    settings.CACHED_MODEL.setInput(blob)
    outputs = settings.CACHED_MODEL.forward(settings.LAST_LAYER_NAMES)

    boxes = []
    confidences = []
    class_ids = []

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > settings.CONFIDENCE:
                box = detection[:4] * np.array([w, h, w, h])
                center_x, center_y, width, height = box.astype('int')

                x = int(center_x - (width / 2))
                y = int(center_y - (height / 2))

                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    idxs = cv2.dnn.NMSBoxes(boxes, confidences, settings.CONFIDENCE, settings.THRESHOLD)
    if len(idxs) > 0:
        for i in idxs.flatten():
            if class_ids[i] == settings.FULL:
                full_cnt += 1
            else:
                empty_cnt += 1

    return full_cnt, empty_cnt

