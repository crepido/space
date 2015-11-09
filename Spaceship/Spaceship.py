__author__ = 'tobias'

from src.Camera import Camera
from src.ComDevice import ComDevice

import time
import Queue
import logging


class Spaceship:
    def __init__(self):
        logging.info("Starting Spaceship")
        self.q_mode_camera = Queue.Queue()
        self.q_com_device_in = Queue.Queue()
        self.q_com_device_out = Queue.Queue()

        self.camera = Camera(self.q_mode_camera)
        self.com_device = ComDevice(self.q_com_device_in, self.q_com_device_out)
        self.running = True

    def set_mode(self, mode):
        logging.info("Setting mode "+mode)
        self.q_mode_camera.put(mode)
        self.q_com_device_in.put(mode)

    def shutdown(self):
        print("Shutting down...")
        self.running = False
        self.set_mode("EXIT")
        logging.info("All shut down")
        logging.info("Shutdown Spaceship")

    def check_queue(self):
        try:
            msg = self.q_com_device_out.get_nowait().upper()
            if msg == "MODE 1" \
                    or msg == "MODE 2" \
                    or msg == "MODE 3" \
                    or msg == "MODE 4" \
                    or msg == "MODE 5" \
                    or msg == "START":
                self.set_mode(msg)
            elif msg == "EXIT":
                self.shutdown()
        except Queue.Empty:
            None
        finally:
            pass

    def run(self):

        logging.info('Started')
        self.com_device.start()
        self.camera.start()

        try:
            while self.running:
                self.check_queue()
                time.sleep(1)

        except KeyboardInterrupt:
            self.shutdown()
        finally:
            pass
        logging.info('Finished')

if __name__ == '__main__':
    logging.basicConfig(filename='/home/pi/space.log', format='%(asctime)s %(levelname)s : %(name)s : %(message)s', level=logging.DEBUG)
    space = Spaceship()
    space.run()