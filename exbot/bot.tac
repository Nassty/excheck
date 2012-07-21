import sys
from twisted.application import service
from twisted.words.protocols.jabber import jid
from wokkel.client import XMPPClient
from settings import BOT_EMAIL, BOT_PASSWORD


from exbot.bot import RedisMessager

application = service.Application("echobot")



xmppclient = XMPPClient(
    jid.internJID(BOT_EMAIL), BOT_PASSWORD)

xmppclient.logTraffic = False
echobot = RedisMessager()
echobot.setHandlerParent(xmppclient)
xmppclient.setServiceParent(application)

