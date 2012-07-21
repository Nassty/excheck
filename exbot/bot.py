from twisted.words.xish import domish
from wokkel.xmppim import MessageProtocol, AvailablePresence
from twisted.internet import defer
from twisted.python import log
from twisted.internet.protocol import ClientCreator
from txredis.protocol import RedisSubscriber
from txredis.protocol import Redis
from twisted.internet import reactor
import json

import commands
import utils

class Subscriber(RedisSubscriber):

    bot = None

    def connectionLost(self, *args):
        print 'connection lost'

    def messageReceived(self, channel, message):
        if self.bot:
            self.bot.write(self.format_message(message))

    def format_message(self, message):
        return """Got a {type} on {ip}
Traceback:
{traceback}
""".format(**json.loads(message))

class RedisMessager(MessageProtocol):

    def __init__(self, *args, **kwargs):
        MessageProtocol.__init__(self, *args, **kwargs)
        self.running = True
        self.emails = []

    def connectionMade(self):
        self.send(AvailablePresence())

        subscriber = ClientCreator(reactor, Subscriber)
        d = subscriber.connectTCP("localhost", 6379)

        @d.addCallback
        def cb(protocol):
            protocol.bot = self
            protocol.subscribe('messages')

        self.redis = ClientCreator(reactor, Redis)
        d = self.redis.connectTCP('localhost', 6379)

    def onMessage(self, msg):
        if msg["type"] == 'chat' and hasattr(msg, "body"):
            cmd_list = str(msg.body).split(" ")
            cmd = cmd_list[0]
            args = cmd_list[1:]
            kwargs = {}
            if "=" in cmd:
                args = []
                kwargs = utils.str_to_dict(" ".join(cmd_list[1:]))

            commands.get_command(cmd)(self, msg, *args, **kwargs)

    def write(self, contents, dest=None):
        emails = self.emails
        if dest:
            emails = [dest]

        for email in emails:
            msg = domish.Element((None, "message"))
            msg['type'] = 'chat'
            msg['to'] = email
            msg.addElement('body', content=contents)
            d = defer.Deferred()
            d.addCallback(log.msg)
            reactor.callLater(0, self.send, msg)
