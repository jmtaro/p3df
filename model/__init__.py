# -*- coding: utf-8 -*-

import sqlite3
import os.path as P

def connect():
    return sqlite3.connect(DATA_FILE)

# private

DATA_DIR = P.join( P.dirname( P.dirname( P.abspath(__file__) ) ) , 'data')# ../data
DATA_FILE = P.join(DATA_DIR, 'p3df_data.sqlite3')

