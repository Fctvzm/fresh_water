import base64
import json
import datetime

import redis
import telegram
from PIL import Image
from io import BytesIO
import numpy as np
from channels.generic.websocket import WebsocketConsumer

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache

from . import utils

REPLY_MSG = str(_('{} full and {} empty bottles left\nStatus: {}\n'))

bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)


class WaterConsumer(WebsocketConsumer):

    def connect(self):
        self.accept()

    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        msg = json.loads(text_data)
        print('Received {} messages of length {}'.format(msg['type'], len(text_data)))
        if msg['type'] == 'ALL_STATE':
            pass
        elif msg['type'] == 'NULL':
            self.send('{"type": "NULL"}')
        elif msg['type'] == 'FRAME':
            self.process_frame(msg['dataURL'])
            self.send('{"type": "PROCESSED"}')
        else:
            print("Warning: Unknown message type: {}".format(msg['type']))

    def validate_to_send(self, full_cnt, empty_cnt):
        today = datetime.datetime.now().day
        refill_date = cache.get(settings.REDIS_REFILL_KEY)
        print(refill_date)
        success_date = cache.get(settings.REDIS_SUCCESS_KEY)

        if empty_cnt == settings.N_BOTTLES and (refill_date is None or int(refill_date) != today):
            cache.set(settings.REDIS_REFILL_KEY, today)
            return REPLY_MSG.format(full_cnt, empty_cnt, str(_('refill')))
        elif full_cnt == settings.N_BOTTLES and (success_date is None or int(success_date) != today):
            cache.set(settings.REDIS_SUCCESS_KEY, today)
            return REPLY_MSG.format(full_cnt, empty_cnt, str(_('success')))
        else:
            return None

    def process_frame(self, data_url):
        head = "data:image/jpeg;base64,"
        assert (data_url.startswith(head))
        data_url = data_url[len(head):]
        img_data = base64.b64decode(data_url)
        img_f = BytesIO()
        img_f.write(img_data)
        img_f.seek(0)
        img = Image.open(img_f)
        frame = np.fliplr(np.asarray(img))

        full_cnt, empty_cnt = utils.count_bottles(frame)

        msg = self.validate_to_send(full_cnt, empty_cnt)
        if msg:
            self.send_info_telegram(img, msg)
        print(full_cnt)
        print(empty_cnt)

    def send_info_telegram(self, image, msg):
        bot.send_message(settings.WATER_CHAT_ID, msg)
        bio = BytesIO()
        bio.name = 'image.jpeg'
        image.save(bio, 'JPEG')
        bio.seek(0)
        bot.send_photo(settings.WATER_CHAT_ID, photo=bio)

