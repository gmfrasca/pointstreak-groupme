from interfaces.rest import main as start_rest_bots
from interfaces.timed import main as start_timed_bots
from time import sleep
import logging
import thread

LOG_FILE = '/var/log/psgroupme.log'

try:
    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)
except IOError:
    # Permission Denied to file, just log to Consolidate
    logging.basicConfig(level=logging.DEBUG)
    logging.warning("Could not log to {0}, logging to console instead".format(
        LOG_FILE))


def main():
    try:
        thread.start_new_thread(start_rest_bots, ())
        thread.start_new_thread(start_timed_bots, ())
    except Exception as e:
        logging.error("Unable to start thread")
        logging.error(e)

    running = True
    while running:
        try:
            sleep(1)
        except KeyboardInterrupt:
            running = False


if __name__ == '__main__':
    main()
