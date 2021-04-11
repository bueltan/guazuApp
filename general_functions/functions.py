import base64
import logging
from datetime import datetime
import re
import shutil
from functools import lru_cache


def get_nodes(subscription):
    nodes = {'node2': '@', 'node3': '#', 'node4': '.'}
    for n in nodes:
        if subscription.find(nodes[n]) != -1:
            nodes[n] = nodes[n] + subscription.split(nodes[n])[1]
            if nodes[n].find("#") != -1 or nodes[n].find("@") != -1:
                nodes[n] = nodes[n].split(".")[0]
            if nodes[n].find("@") != -1:
                nodes[n] = nodes[n].split("#")[0]
        else:
            nodes[n] = ''
    return nodes


def get_code_entity(id_name):
    id_name = id_name.encode('ascii')
    id_code = base64.standard_b64encode(id_name)
    id_code = id_code.decode("utf-8")
    return id_code


def decode(id):
     return (base64.standard_b64decode(id)).decode("utf-8").split(":")[1]


def encode(id):
    message = id
    message_bytes = message.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('utf-8')
    return base64_message


def format_text(text):
    text = re.sub(' +', ' ', text)
    return text


def count_lent_sentence(text):
    count = 0
    sentence = ""
    parcial = 0
    for character in text:
        if character != "\n":
            sentence += character
            parcial = len(sentence)
        else:
            if parcial > count:
                count = len(sentence)
                sentence = ""

    if parcial > count:
        count = len(sentence)

    return count


def get_extension(type):
    if type == 'audio':
        extension = '.ogg'

    if type == 'image':
        extension = '.png'

    return extension


def get_resolution_img(url):
    size = url.split("size=")[1]
    width = int(size.split("x")[0])
    height = int(size.split("x")[1])
    return width, height


def get_height_img(width, height, width_end):
    percent = 100 * float(width_end) / float(width)
    height_end = round(height / 100 * percent)
    return width_end, height_end


def save_dir_in_db(dir, table):
    pass


def copy(src_file, dest_file):
    shutil.copy2(src_file, dest_file, follow_symlinks=True)


class TimeFormat(object):

    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.day_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        self.dias_semanas = ['lun', 'mar', 'mie', 'jue', 'vie', 'sab', 'dom']
    @lru_cache
    def date_with_days_es(self):
        try:
            dt_object = datetime.fromtimestamp(self.timestamp)
            str_time = dt_object.strftime(" %a %d %H:%M ")

            for index, day in enumerate(self.day_week):
                if day in str_time:
                    str_time = str_time.replace(day, self.dias_semanas[index])
                    break
        except Exception as error:
            logging.error(f"Error in time_am_pm {error} ")
            str_time = 'time_error'
        return str_time
    @lru_cache
    def time_am_pm(self):
        try:
            dt_object = datetime.fromtimestamp(self.timestamp)
            str_time = dt_object.strftime("%H:%M %p")
        except Exception as error:
            logging.error(f"Error in time_am_pm {error} ")
            str_time = 'time_error'
        return str_time

