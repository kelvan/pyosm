#!/usr/bin/env python

import sqlite3
from xml.dom.minidom import parse

class SqliteConnector:
    def __init__(self, path='stations.db'):
        self.conn = sqlite3.connect(path)

    def create_db(self):
        c = self.conn.cursor()

        try:
            c.execute('''create table stations
                (osmid INTEGER PRIMARY KEY, name TEXT, lat REAL, lon REAL)''')
        except sqlite3.OperationalError as e:
            print e.message
        try:
            c.execute('''create table lines
                (osmid INTEGER PRIMARY KEY, name TEXT)''')
        except sqlite3.OperationalError as e:
            print e.message
        try:
            c.execute('''create table relation
                (station_id INTEGER, line_id INTEGER)''')
        except sqlite3.OperationalError as e:
            print e.message

        self.conn.commit()
        c.close()

    def insert_station(self, t):
        """ Takes tuple or list of tuples t
        (osmid, stationname, latitude, lontitude)
        insert into sqlite db if doesn't exist
        """
        if type(t) == tuple:
            t = [t]

        c = self.conn.cursor()
        for s in t:
            try:
                c.execute('INSERT INTO stations VALUES (?,?,?,?)', s)
            except sqlite3.OperationalError as e:
                print e.message

        self.conn.commit()
        c.close()

    def insert_line(self, t):
        """ (osmid, line_id, [station_ids])
        non existing station_ids are ignored
        """
        if type(t) == tuple:
            t = [t]

        c = self.conn.cursor()
        for l in t:
            c.execute('INSERT INTO lines VALUES (?,?)', l[:2])
            lineid = c.lastrowid
            for s in l[2]:
                try:
                    c.execute('insert into relation values (?,?)', (s, lineid))
                except sqlite3.OperationalError as e:
                    print e.message

        self.conn.commit()
        c.close()

class XmlExtractor:
    def __init__(self, filename):
        self.dom = parse(filename)
        self.sql = SqliteConnector()
        self.sql.create_db()

    def sql_insert(self):
        for node in self.dom.firstChild.childNodes:
            if node.nodeName == 'node':
                try:
                    stationname = filter(lambda x: x.nodeName == 'tag' and x.attributes['k'].value == 'name', node.childNodes)[0].attributes['v'].value
                    print stationname
                    self.sql.insert_station((node.attributes['id'].value, stationname, node.attributes['lat'].value, node.attributes['lon'].value))
                except Exception as e:
                    print e.message

    @property
    def stationnames(self):
        r = []
        for node in self.dom.firstChild.childNodes:
            if node.nodeName == 'node':
                try:
                    stationname = filter(lambda x: x.nodeName == 'tag' and x.attributes['k'].value == 'name', node.childNodes)[0].attributes['v'].value
                    r.append(stationname)
                except Exception as e:
                    print e.message
        return list(set(r))
