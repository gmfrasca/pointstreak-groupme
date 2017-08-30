from psgroupme.responder import Responder
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--message', dest='message', default='Hello World')
parser.add_argument('-b', '--bot_id', dest='bot_id', required=True)

args = parser.parse_args()
print(args.message)
