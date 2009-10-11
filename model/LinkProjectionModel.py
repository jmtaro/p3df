# -*- coding: utf-8 -*-

import time as t
import __init__ as model

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

info, warn, error = model.logging('[LinkProjectionModel]')

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

    def delete(self, expire=None):
        query = 'DELETE FROM link_projection WHERE '
        where, value = [], {}
        if expire is not None:
            where.append('expire_timestamp < :expire')
            value['expire'] = expire
        self._conn.execute(query + ' AND '.join(where), value)

