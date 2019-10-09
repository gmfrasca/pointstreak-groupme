from psgroupme.interfaces.responder import DebugResponder


class TestTimedBot(object):

    def send_msg(self, msg):
        self.responder = DebugResponder(1)
        if msg and msg != '':
            self.responder.reply(msg)
