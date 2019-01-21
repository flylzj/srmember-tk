# coding: utf-8
import sqlite3


class MyDb:
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename)

    def init_db(self):
        sql = '''
        CREATE TABLE good
        '''