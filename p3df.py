# -*- coding: utf-8 -*-

from twisted.application import service
from twisted.internet import reactor
from twisted.python import log, logfile
from twisted.web import http, proxy

import optparse
import os
import re
import sys
import urllib

class ProxyRequest(proxy.ProxyRequest):
    def requestReceived(self, command, path, version):
        plugin = P3df.getPlugin(command, path, version)
        if plugin:
            self.protocols = {'http' : plugin.HttpProxyClientFactory}
        proxy.ProxyRequest.requestReceived(self, command, path, version)

class Proxy(proxy.Proxy):
    def requestFactory(self, *args):
        return ProxyRequest(*args)

class ProxyFactory(http.HTTPFactory):
    def buildProtocol(self, addr):
        protocol = Proxy()
        return protocol

class Plugin():
    def __init__(self, client_cls):
        class Factory(proxy.ProxyClientFactory):
            def buildProtocol(self, addr):
                client = proxy.ProxyClientFactory.buildProtocol(self, addr)
                client.__class__ = client_cls
                return client
        self.HttpProxyClientFactory = Factory

class P3df():
    @classmethod
    def start(cls):
        params = cls.getParameter()
        cls.clientPattern = {}

        path = os.path.abspath(__file__)
        (dir, name) = (os.path.dirname(path), os.path.basename(path))
        cls.startLogging('p3df.log', os.sep.join([dir, 'log']))

        modulenames = []
        for name in os.listdir( os.sep.join([dir, 'plugin']) ):
            match = re.match('([a-z]+[0-9]*[a-z]*).py$', name)
            if match:
                modulenames.append( match.groups()[0] )

        modules = __import__('plugin', fromlist=modulenames)
        for name in modulenames:
            plugin = getattr(modules, name)
            for (regexp, client_cls) in plugin.getClientPattern().iteritems():
                cls.clientPattern[regexp] = Plugin(client_cls)

        reactor.listenTCP(params.port, ProxyFactory())
        reactor.run()

    @classmethod
    def startLogging(cls, filename, logdir):
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        observer = log.FileLogObserver( logfile.DailyLogFile(filename, logdir) )
        log.startLogging(observer)

    @classmethod
    def getParameter(cls):
        parser = optparse.OptionParser()
        parser.add_option(
            '--port',
            type='int',
            dest='port',
            help='port for request to be listened'
        )
        (opts, args) = parser.parse_args()
        required_keys = [
            'port',
        ]
        for i in required_keys:
            if not getattr(opts, i):
                parser.print_help()
                exit(2)# syntax error
        return opts

    @classmethod
    def getPlugin(cls, command, path, version):
        for (regexp, plugin) in cls.clientPattern.iteritems():
            if re.match(regexp, path):
                return plugin

if __name__ == "__main__":
    P3df.start()
