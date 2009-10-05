# -*- coding: utf-8 -*-

import os.path as P
import model

class Updater():
    def __init__(self, conn):
        self._args = []
        self._conn = conn
    def next(self, fn_list):
        self._args.append(fn_list)
    def execute(self):
        for fn_list in self._args:
            for fn in fn_list:
                print '[call]' , fn.__name__
                fn(self._conn)
        self._conn.commit()
        self._conn.close()
        print '[done]' , P.basename(__file__)

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
    u = Updater( model.connect() )
    u.next([
        create_table_link_projection,
        create_table_response_cache,
    ])
    u.execute()

if __name__ == "__main__":
    start()

