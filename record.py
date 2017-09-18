#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

import logging
import os.path
logfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log.txt')
logging.basicConfig(filename = logfile, level = logging.INFO, format = '%(asctime)s %(levelname)s %(threadName)-10s %(message)s')

import os
import time
from datetime import datetime

import subprocess
import telegram
import RPi.GPIO as GPIO
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


token = '317386xxx:xxxxxxx'
group_info = {'id': -10xxxxx87, 'name': 'Raspberry XXX'}
bot = telegram.Bot(token)
file_path = './files'

# record voice

GPIO.setmode(GPIO.BOARD)
GPIO.setup(18, GPIO.OUT, initial = GPIO.LOW) # set pin18 output 
GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)  # set pin19 input

def get_arecord_pid():
    command = "ps aux | grep arecord | grep -v grep | awk '{print $2}'"
    pid = subprocess.check_output(command, shell = True)
    pid = pid.decode('utf-8').strip('\n')
    return pid

# flag open or close
led_flag = False

# start time
start_time = None

# file name
file_name = None

def start_process(channel):
    global start_time
    global file_name
    global led_flag
    led_flag = not led_flag
    if led_flag:
        start_time = time.time()
        GPIO.output(18, GPIO.HIGH)
        current_time = datetime.today().strftime("%Y%m%d-%X")
        file_name = current_time + '.{}'
        logging.info('start record: {}'.format(file_name))
        #command = 'arecord -D plughw:1,0 -f cd -t wav > /home/pi/telegram/tmp/{}.wav &'.format(current_time)
        command = 'arecord -D plughw:1,0 -f S16_LE -t wav > /home/pi/telegram/tmp/{}.wav &'.format(file_name)
        logging.info(command)
        subprocess.call(command, stdout = subprocess.PIPE, shell = True)
    else:
        pid = get_arecord_pid()
        if pid:
            duration = int(time.time() - start_time)
            command = 'kill {}'.format(pid)
            subprocess.call(command, shell = True)
            mv = 'mv /home/pi/telegram/tmp/{}.wav /home/pi/telegram/files/{}.wav'.format(file_name, file_name.format(duration))
            subprocess.call(mv, shell = True)

        GPIO.output(18, GPIO.LOW)
        logging.info('stop record')
     
GPIO.add_event_detect(19, GPIO.BOTH, callback = start_process)


# watch and send voice
class MyFileSystemEventHandler(FileSystemEventHandler):

    def __init__(self, fn):
        super().__init__()
        self.fn = fn
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".wav"):
            logging.info("detect new file created...")
            self.fn(event.src_path)


def send_message(real_path):
    if not os.path.exists(real_path):
        logging.info('{} file not found, return...'.format(real_path))
        return
    _, duration, _ = real_path.split('.')
    bot.send_voice(chat_id = group_info['id'], voice = open(real_path, 'rb'), duration = duration, timeout = 120)
    logging.info('{}, send file finish...'.format(real_path))
    #dest_file = os.path.join(os.path.abspath(backup_path), os.path.basename(real_path))
    #logging.info('\nsource:{}\ndest:{}'.format(real_path, dest_file))
    #os.rename(real_path, dest_file)

if __name__ == '__main__':
    real_path = os.path.abspath(file_path)
    #logging.info(real_path)

    observer = Observer()
    observer.schedule(MyFileSystemEventHandler(send_message), real_path, recursive = False)
    observer.start()

    logging.info('Watching direction {}...'.format(real_path))
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

GPIO.cleanup()
