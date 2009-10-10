# -*- coding: utf-8 -*-

import time as t
from twisted.python import log

def createInstance(conn):
    return Model(conn)

class Record():
    def __init__(self, url='', path='', expire=0):
        self.url = url
        self.path = path
        (self.expire_timestamp, self.expire_string) = self._calc_exp(expire)
    def toDict(self):
        return {
            'url': self.url,
            'path': self.path,
            'expire_timestamp': self.expire_timestamp,
            'expire_string': self.expire_string,
        }
    def _calc_exp(self, expire):
        if expire:
            sec = int( t.time() + expire )
            return ( sec, t.strftime("%Y-%m-%dT%H:%M:%SZ", t.gmtime(sec)) )# rfc3339
        else:
            return ( 0, '' )
# private

def info(*args):
    log.msg( "[LinkProjectionModel]%s" % ":".join( str(arg) for arg in args ) )
def warn(*args):
    info('[warning]', *args)

class Model():
    def __init__(self, conn):
        self._conn = conn

    def find(self, url):
        query = 'SELECT * FROM link_projection WHERE url=?'
        result = self._conn.execute(query, [url])
        return result.fetchone()

    def exist(self, url):
        return self.find(url) is not None

    def put(self, record):
        if self.exist(record.url):
            self.update(record)
        else:
            self.register(record)

    def register(self, record):
        query = 'INSERT INTO link_projection(url, path, expire_timestamp, expire_string) '
        query += 'VALUES(:url, :path, :expire_timestamp, :expire_string)'
        self._conn.execute(query, record.toDict())

    def update(self, record):
        ls = []
        if record.path:
            ls.append('path=:path')
        if record.expire_timestamp:
            ls.append('expire_timestamp=:expire_timestamp')
            ls.append('expire_string=:expire_string')
        query = 'UPDATE link_projection SET %s WHERE url=:url ' % ','.join(ls)
        self._conn.execute(query, record.toDict())

