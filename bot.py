from twisted.words.protocols import irc
from twisted.internet import protocol, task, threads, reactor
from twisted.internet.protocol import Protocol, ClientCreator
from twisted.python import log
from twisted.python import rebuild
from collections import defaultdict

from actions import actions
import json
import urllib2
import MySQLdb
import sys
from time import time


specialAdmins = [
   # Names here
   'Killerhands',
]


class KenBot(irc.IRCClient):

    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    #TODO: Are these essential?
    def _idle_ping(self):
        self.factory.log.log(logging.DEBUG - 5, 'Sending idle PING')
        self.ping_deferred = None
        self.reconnect_deferred = reactor.callLater(self.factory.pong_timeout, self._timeout_reconnect)
        self.msg('PING idle-ibid')
    
    def irc_PONG(self, prefix, params):
        if params[-1] == 'idle-ibid' and self._reconnect_deferred is not None:
            self.factory.log.log(logging.DEBUG - 5, 'Received PONG')
            self._reconnect_deferred.cancel()
            self._reconnect_deferred = None
            self._ping_deferred = reactor.callLater(self.factory.ping_interval, self._idle_ping)

    def signedOn(self):
        self.join(self.factory.channel)
        self.active = True
        self.liveFlag = True
        self.admins = specialAdmins

        #task.LoopingCall(self.updateAdmins).start(120)
        print "Signed on as %s." % (self.nickname,)
    
    def joined(self, channel):
        print "Joined %s." % (channel,)

    def modeChanged(self, user, channel, set, modes, args):
        try:
            users = ' '.join(args) 
        except:
            users = ''
        print "%s mode changed to %s for: [%s]" % (user, modes, users)
        if modes == 'o':
            for mod in args:
                if mod not in self.admins:
                    self.admins.append(mod)
                    print >>sys.__stdout__, 'Admins: [' + ' '.join(self.admins) + ']'
    
    #TODO: Why (not) lower()?
    def privmsg(self, user, channel, msg):
        #pollActive = False
        nick = user.split("!",1)[0]
        self.nick = nick
        nickLow = nick.lower()
        print nick + ': ' + msg
        self.msgRaw = msg
        msg = msg.lower()

        for action in actions:
            if action.act(channel, nick, msg, self):
                break

    msgLog = {}

    def msg(self, chan, text, format=None, cooldown=0):
        if text in self.msgLog:
            prevTime = self.msgLog[text]
        else:
            prevTime = 0.0
        currTime = time()

        #print prevTime
        
        if ((prevTime + float(cooldown)) > currTime):
            print 'spam found'
            return
        
        self.msgLog[text] = time()
        #print time()
        
        if format:
            irc.IRCClient.msg(self, chan, text % format)
        else:
            irc.IRCClient.msg(self, chan, text)
            
    
    def updateAdmins(self):
        print 'Updating admins... ',
        self.admins = specialAdmins
        print ' '.join(self.admins)

class KenBotFactory(protocol.ClientFactory):
    protocol = KenBot
    
    def __init__(self, channel, nickname='Killer|BoT'):
        self.channel = channel
        self.nickname = nickname
    
    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()
    
    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)


import sys
from twisted.internet import reactor

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    chan = sys.argv[1]
    reactor.connectTCP('irc.uk.quakenet.org', 6667, KenBotFactory('#' + chan))
    reactor.run()
