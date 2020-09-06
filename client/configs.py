import os

SOCKET_SERVER = "127.0.0.1"  # Server ip-address
SOCKET_PORT = 8000  # Server Port
SOCKET_URL = "ws://{0}/ws/water-count-stream/".format(SOCKET_SERVER).format(":").format(SOCKET_PORT)

# http://admin:admin@192.168.1.101/video.mjpg?mute
MJPG_IP_CAM_URL = "http://192.168.1.101/video.mjpg?mute"
MJPG_USERNAME, MJPG_PASSWORD = "admin", "admin"


WAIT_SECONDS = 300

CHUNK_SIZE = 1024

NOT_RECOGNIZED = "Not recognized!"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOGGING_FILE = os.path.join(BASE_DIR, 'debug.log')
