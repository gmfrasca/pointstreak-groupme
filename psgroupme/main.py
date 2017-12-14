from rest import main as start_rest_bots
from timed import main as start_timed_bots
import thread


def main():
    try:
        thread.start_new_thread(start_rest_bots, ())
        thread.start_new_thread(start_timed_bots, ())
    except Exception as e:
        print "Error: unable to start thread"
        print e

    while 1:
        pass


if __name__ == '__main__':
    main()
