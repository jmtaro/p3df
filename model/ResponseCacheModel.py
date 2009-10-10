# -*- coding: utf-8 -*-

import time as t

def createInstance(conn):
    return Model(conn)

class Record():
    def __init__(self, url='', data=None, expire=0):
        self.url = url
        self.data = buffer(data)
        (self.expire_timestamp, self.expire_string) = self._calc_exp(expire)
    def toDict(self):
        return {
            'url': self.url,
            'data': self.data,
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

class Model():
    def __init__(self, conn):
        self._conn = conn

    def find(self, url):
        query = 'SELECT * FROM response_cache WHERE url=?'
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
        query = 'INSERT INTO response_cache(url, data, expire_timestamp, expire_string) '
        query += 'VALUES(:url, :data, :expire_timestamp, :expire_string)'
        self._conn.execute(query, record.toDict())

    def update(self, record):
        ls = []
        if record.url:
            ls.append('data=:data')
        if record.expire_timestamp:
            ls.append('expire_timestamp=:expire_timestamp')
            ls.append('expire_string=:expire_string')
        query = 'UPDATE response_cache SET %s WHERE url=:url ' % ','.join(ls)
        self._conn.execute(query, record.toDict())

