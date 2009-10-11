# -*- coding: utf-8 -*-
import sqlite3
import os.path as P
from time import time

from twisted.python import log

def connect():
    conn = sqlite3.connect(DATA_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def deleteExpired():
    current = time()
    conn = connect()
    try:
        LinkProjectionModel.createInstance(conn).delete(expire=current)
        ResponseCacheModel.createInstance(conn).delete(expire=current)
        conn.commit()
    except Exception, e:
        log.msg('[deletion-error]', e)
        conn.rollback()
    finally:
        conn.close()

def logging(key):
    def msg(key): return lambda *args: log.msg( key + ":".join( str(i) for i in args ) )
    return ( msg('[info]'), msg('[warning]'), msg('[error]') )

# private

DATA_DIR = P.join( P.dirname( P.dirname( P.abspath(__file__) ) ) , 'data')# ../data
DATA_FILE = P.join(DATA_DIR, 'p3df_data.sqlite3')

