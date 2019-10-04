from psgroupme.interfaces.rest import main as start_rest_bots
from psgroupme.interfaces.timed import main as start_timed_bots
from time import sleep
import argparse
import logging
import _thread

LOG_FILE = './log/psgroupme.log'


def setup_logging(debug=False, logfile=LOG_FILE, console=False):
    level = logging.DEBUG if debug else logging.INFO
    stdout_fmt = '[%(asctime)s][%(levelname)s][%(name)s]: %(message)s'
    cfg = {'level': level, 'format': stdout_fmt}
    if logfile is not None and console is False:
        cfg.update({'filename': logfile})
    logging.basicConfig(**cfg)

    if debug:
        logging.info("Debug Mode On")

    if console or logfile is None:
        logging.info("Logging to Console Only")
    else:
        cfg.update({'filename': logfile})
        logging.info("Logging to {}".format(logfile))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log_file', default=LOG_FILE)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument("--console", action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging(args.verbose, args.log_file, args.console)
    try:
        _thread.start_new_thread(start_rest_bots, ())
        _thread.start_new_thread(start_timed_bots, ())
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
