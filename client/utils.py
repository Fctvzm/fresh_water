import json
import time
import base64
import logging
import urllib3
import requests

import configs

prev = time.time()


def is_valid_img(cur):
    global prev
    print(cur - prev)
    if cur - prev >= configs.WAIT_SECONDS:
        prev = cur
        return True
    return False


def send_img(image, socket_protocol):
    cur = time.time()
    if is_valid_img(cur):
        dataURL = 'data:image/jpeg;base64,{}'.format(base64.b64encode(image).decode())
        msg = {'type': 'FRAME', 'dataURL': dataURL}
        socket_protocol.sendMessage(payload=bytes(json.dumps(msg).encode("utf-8")))


def use_mjpg_con(socket_protocol, ip_cam_url=configs.MJPG_IP_CAM_URL,
                 username=configs.MJPG_USERNAME, password=configs.MJPG_PASSWORD):
    try:
        r = requests.get(ip_cam_url, auth=(username, password), stream=True)
        if r.status_code == 200:
            bytes_ = bytes()
            for chunk in r.iter_content(chunk_size=configs.CHUNK_SIZE):
                bytes_ += chunk
                a = bytes_.find(b'\xff\xd8')
                b = bytes_.find(b'\xff\xd9')
                if a != -1 and b != -1:
                    image = bytes_[a:b + 2]
                    bytes_ = bytes_[b + 2:]
                    send_img(image, socket_protocol)
    except (urllib3.exceptions.HeaderParsingError, requests.exceptions.ConnectionError) as e:
        logging.info("Exception with connection to camera: {}".format(e))
        use_mjpg_con(socket_protocol, ip_cam_url, username, password)
    else:
        logging.info("Received unexpected status code {}".format(r.status_code))
