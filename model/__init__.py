# -*- coding: utf-8 -*-

import sqlite3
import os.path as P

def connect():
    conn = sqlite3.connect(DATA_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# private

DATA_DIR = P.join( P.dirname( P.dirname( P.abspath(__file__) ) ) , 'data')# ../data
DATA_FILE = P.join(DATA_DIR, 'p3df_data.sqlite3')

