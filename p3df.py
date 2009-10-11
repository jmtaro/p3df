# -*- coding: utf-8 -*-

from twisted.internet import reactor
from twisted.python import log, logfile
from twisted.web import http, proxy

import optparse
import os
import re
from glob import glob

import model

DIR_CORE = os.path.dirname( os.path.abspath(__file__) )
DIR_DATA = os.path.join(DIR_CORE, 'data')
DIR_PLUGIN = os.path.join(DIR_CORE, 'plugin')

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
        cls.clientPattern = {}
        cls.startLogging('p3df.log', DIR_DATA)

        modulenames = []
        for name in os.listdir(DIR_PLUGIN):
            match = re.match('([a-z]+[0-9]*[a-z]*).py$', name)
            if match:
                modulenames.append( match.groups()[0] )

        modules = __import__('plugin', fromlist=modulenames)
        for name in modulenames:
            plugin = getattr(modules, name)
            for (regexp, client_cls) in plugin.getClientPattern().iteritems():
                cls.clientPattern[regexp] = Plugin(client_cls)

        params = cls.getParameter()
        reactor.callLater(1, GC().execute)
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

class GC():
    def __init__(self):
        self._freq_sec = 60 * 60
        self._log_count = 7
    def execute(self):
        self._for_log()
        self._for_db()
        log.msg('[GC-executed]')
        reactor.callLater(self._freq_sec, self.execute)
    def _for_log(self):
        def by_mtime(a, b):
            return cmp( os.path.getmtime(a), os.path.getmtime(b) )
        ls = glob(os.path.join(DIR_DATA, 'p3df.log.*'))
        ls.sort(by_mtime, reverse=True)
        map(os.remove, ls[self._log_count:])
    def _for_db(self):
        model.deleteExpired()

if __name__ == "__main__":
    P3df.start()

