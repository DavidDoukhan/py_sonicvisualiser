# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 David Doukhan <david.doukhan@gmail.com>

# This file is part of py_sonicvisualiser.

# py_sonicvisualiser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# py_sonicvisualiser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with TimeSide.  If not, see <http://www.gnu.org/licenses/>.

# Author: David Doukhan <david.doukhan@gmail.com>


import xml.sax as sax
import xml.dom.minidom as minidom
from SVDataset import SVDataset2D, SVDataset3D

class SVContentHandler(sax.ContentHandler):
    """
    Goal: clone to dom at the exception of dataset nodes
    """
    def __init__(self):
        sax.ContentHandler.__init__(self)
        self.datasets = []
        imp = minidom.getDOMImplementation()
        dt = imp.createDocumentType('sonic-visualiser', None, None)
        self.dom = imp.createDocument(None,'sv', dt)
        self.curnode = self.dom.documentElement        
        self.nbdata = 0
 
    def startElement(self, name, attrs):
        ## TODO MANAGE LAYER presentationName

        if name in ['model', 'dataset', 'layer']:
            self.nbdata += 1

        if name == 'model' and attrs.has_key('mainModel') and attrs.getValue('mainModel') == 'true':
            self.samplerate = int(attrs.getValue('sampleRate'))
            self.nframes = int(attrs.getValue('end'))
            self.mediafile = attrs.getValue('file')

        if name == 'dataset':
            dim = int(attrs.getValue('dimensions'))
            dataid = attrs.getValue('id')
            if dim == 2:
                self.datasets.append(SVDataset2D(self.dom, dataid, self.samplerate))
            elif dim == 3:
                self.datasets.append(SVDataset3D(self.dom, dataid, self.samplerate))
            self.curnode = self.curnode.appendChild(self.datasets[-1])
        elif name == 'point':
            self.datasets[-1].append_xml_point(attrs)
        elif name == 'sv':
            pass
        else:
            node = self.curnode.appendChild(self.dom.createElement(name))

            if name == 'data':
                self.data = node
            elif name == 'display':
                self.display = node
            elif name == 'selections':
                self.selections = node
            elif name == 'window':
                self.defwidth = int(attrs.getValue('width'))

            for at, val in attrs.items():
                node.setAttribute(at, val)
            self.curnode = node

    def endElement(self, name):
        if name == 'point':
            pass
        elif name == 'sv':
            pass
        else:
            self.curnode = self.curnode.parentNode
