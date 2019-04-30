from psgroupme.responder import Responder
import argparse
import logging

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--message', dest='message', default='Hello World')
parser.add_argument('-b', '--bot_id', dest='bot_id', required=True)

args = parser.parse_args()
resp = Responder(args.bot_id)
resp.reply(args.message)
logging.basicConfig(level=logging.INFO)
logging.info(args.message)
