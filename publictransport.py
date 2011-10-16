#!/usr/bin/env python

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from codecs import open
import sys
from datetime import datetime

class PublicTransportExtractHandler(ContentHandler):
    """ Extract public transport related information from osm file
    """
    def __init__(self):
        # content of current node
        self.nodeContent = {}
        self.nodeAttributes = {}
        self.members = []
        # node identified as public transport tag
        self.isPublicTransport = False
        t = datetime.now()
        fn = 'public_transport_%s_%s:%s.xml' % (t.date(), t.hour, t.minute)
        self._writer = open(fn, 'w', "utf-8")
        self._writer.write('<?xml version="1.0" encoding="UTF-8"?>\n')

    def startElement(self, name, attrs):
        if name == 'node':
            self.nodeAttributes = attrs

        elif name == 'relation':
            self.nodeAttributes = {'id': attrs['id'], 'uid': attrs['uid']}

        elif name == 'member':
            self.members += [attrs]

        elif name == 'tag':
            self.nodeContent[attrs['k']] = attrs['v']

            if (attrs['k'] == 'highway' and attrs['v'] == 'bus_stop') or \
                (attrs['k'] == 'railway' and (attrs['v'] == 'tram_stop' or attrs['v'] == 'halt')) or \
                (attrs['k'] == 'type' and attrs['v'] == 'public_transport'):
                self.isPublicTransport = True

        elif name == 'osm':
            self._writer.write("<osm>\n")

    def endElement(self, name):
        if name == "node":
            if self.isPublicTransport:
                self._writer.write('<node id="{id}" lat={lat} lon={lon}>\n'.format(**self.nodeAttributes))
                for key, value in self.nodeContent.items():
                    self._writer.write('<tag k="%s" v="%s"/>\n' % (key, value))
                self._writer.write('</node>\n')
            self.reset()

        elif name == "relation":
            if self.isPublicTransport:
                self._writer.write('<relation id="{id}" uid={uid}\n'.format(**self.nodeAttributes))
                for key, value in self.nodeContent.items():
                    self._writer.write('<tag k="%s" v="%s"/>\n' % (key, value))
                for member in self.members:
                    self._writer.write('<member type="{type}" ref="{ref}" role="{role}"/>\n'.format(**member))
                self._writer.write('</relation>\n')
            self.reset()


    def endDocument(self):
        self._writer.write('</osm>')
        self._writer.close()

    def reset(self):
        self.members = []
        self.nodeAttributes = {}
        self.nodeContent = {}
        self.isPublicTransport = False

if __name__ == "__main__":
    parser = make_parser()
    parser.setContentHandler(PublicTransportExtractHandler())
    parser.parse(sys.argv[1])

