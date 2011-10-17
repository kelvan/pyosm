#!/usr/bin/env python

from gotovienna.utils import *
from gotovienna.realtime import *

itip = ITipParser()

def get_lines():
    return categorize_lines(itip.lines)

def get_stations(line):
    return itip.get_stations(line).items()

def remove_duplicates(lst):
    outlist = []
    for element in lst:
        if element not in outlist:
            outlist.append(element)
    return outlist

def get_all_stations():
    st = {}
    for type, lines in get_lines():
        for line in lines:
            st[line] = {}
            for direction in get_stations(line):
                st[line][direction[0]] = map(lambda x: x[0], direction[1])
    return st

if __name__ == "__main__":
    for type, lines in get_lines():
        print (' %s ' % type).center(79, '*')
        for line in lines:
            for direction in get_stations(line):
                print
                print line + " " + (' %s ' % direction[0]).center(77 - len(line) * 2, '=') + " " + line
                # use remove_duplicates(direction[1]) if necessary 
                for station, _ in direction[1]:
                    print station.center(79)
        print
