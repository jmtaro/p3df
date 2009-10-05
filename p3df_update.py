# -*- coding: utf-8 -*-

import sqlite3
import traceback
import os.path as P

import model

DATA_DIR = P.join( P.dirname( P.abspath(__file__) ) , 'data')

class Upgrader():
    def __init__(self, conn):
        self._current = self._get_current_ver()
        self._args = []
        self._conn = conn
    def next(self, ver, fn_list):
        if ver > self._current:
            self._args.append([ver, fn_list])
    def execute(self):
        for (ver, fn_list) in self._args:
            for fn in fn_list:
                print '[call]' , fn.__name__
                fn(self._conn)
        self._set_current_ver(ver)
        self._conn.commit()
        self._conn.close()
        print '[done]' , P.basename(__file__)

    def _get_current_ver(self):
        return 0.0
    def _set_current_ver(self, ver):
        return

def create_table_link_projection(conn):
    conn.execute('''create table if not exists link_projection(
        url text primary key,
        path text,
        expire_timestamp integer,
        expire_string text
    )''')
    index_expire = 'l3p9_expire'
    query = "select * from sqlite_master where type='index' and name=?"
    if not conn.execute(query, [index_expire]).fetchone():
        conn.execute('create index %s on link_projection(expire_timestamp)' % index_expire)

def create_table_response_cache(conn):
    conn.execute('''create table if not exists response_cache(
        url text primary key,
        data none,
        expire_timestamp integer,
        expire_string text
    )''')
    index_expire = 'r7c4_expire'
    query = "select * from sqlite_master where type='index' and name=?"
    if not conn.execute(query, [index_expire]).fetchone():
        conn.execute('create index %s on response_cache(expire_timestamp)' % index_expire)

def start():
    u = Upgrader( model.connect() )
    u.next(1.0, [
        create_table_link_projection,
        create_table_response_cache,
    ])
    u.next(2.0, [
    ])
    u.execute()

if __name__ == "__main__":
    start()

