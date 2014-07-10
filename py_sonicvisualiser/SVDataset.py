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

"""
This class is allows the storage of large continuous dataset
in xml.dom.minidom documents
"""

import xml.dom.minidom
import collections


class SVDataset2D(xml.dom.minidom.Text):
    """
    This class is aimed at storing large datasets in minidom documents
    datasets are stored as iterable structure (lists, numpy arrays, ...)
    This data is converted to sonic visualiser point nodes at writing time
    This allows to avoid the storage of very large xml trees in RAM,
    and avoid swap 
    """
    def __init__(self, domdoc, datasetid, samplerate):
        self.datasetid = datasetid
        self.frames = []
        self.values = []
        self.labels = []
        self.label2int = dict()
        self.int2label = dict()
        self.ownerDocument = domdoc
        self.dimensions = 2
        self.samplerate = samplerate

    def set_data_from_iterable(self, frames, values, labels=None):
        """
        Initialize a dataset structure from iterable parameters

        :param x: The temporal indices of the dataset
        :param y: The values of the dataset
        :type x: iterable
        :type y: iterable
        """
        if not isinstance(frames, collections.Iterable):
            raise TypeError, "frames must be an iterable"
        if not isinstance(values, collections.Iterable):
            raise TypeError, "values must be an iterable"
        assert(len(frames) == len(values))
        self.frames = frames
        self.values = values
        if labels is None:
            self.label2int['New Point'] = 0
            self.int2label[0] = 'New Point'
            self.labels = [0 for i in xrange(len(frames))]
        else:
            if not isinstance(labels, collections.Iterable):
                raise TypeError, "labels must be an iterable"
            for l in labels:
                if l not in self.label2int:
                    self.label2int[l] = len(self.label2int)
                    self.int2label[len(self.int2label)] = l
                self.labels.append(self.label2int[l])
    
    def append_xml_point(self, attrs):
        self.frames.append(int(attrs.getValue('frame')))
        self.values.append(float(attrs.getValue('value')))
        l = attrs.getValue('label')
        if l not in self.label2int:
            self.label2int[l] = len(self.label2int)
            self.int2label[len(self.int2label)] = l
        self.labels.append(self.label2int[l])
            

    def writexml(self, writer, indent="", addindent="", newl=""):
        """
        Write the continuous  dataset using sonic visualiser xml conventions
        """
        # dataset = self.data.appendChild(self.doc.createElement('dataset'))
        # dataset.setAttribute('id', str(imodel))
        # dataset.setAttribute('dimensions', '2')
        writer.write('%s<dataset id="%s" dimensions="%s">%s' % (indent, self.datasetid, self.dimensions, newl))
        indent2 = indent + addindent
        for l, x, y in zip(self.labels, self.frames, self.values):
            writer.write('%s<point label="%s" frame="%d" value="%f"/>%s' % (indent2, self.int2label[l], x, y, newl))
        writer.write('%s</dataset>%s' % (indent, newl))




class SVDataset3D(SVDataset2D):
    def __init__(self, domdoc, datasetid, samplerate):
        SVDataset2D.__init__(self, domdoc, datasetid, samplerate)
        self.durations = []
        self.dimensions = 3

    def set_data_from_iterable(self, frames, values, durations, labels=None):
        SVDataset2D.set_data_from_iterable(self, frames, values, labels)
        if not isinstance(durations, collections.Iterable):
            raise TypeError, "durations must be an iterable"
        assert(len(self.frames) == len(durations))
        self.durations = durations

    def append_xml_point(self, attrs):
        SVDataset2D.append_xml_point(self, attrs)
        self.durations.append(float(attrs.getValue('duration')))

    def writexml(self, writer, indent="", addindent="", newl=""):
        """
        Write the continuous  dataset using sonic visualiser xml conventions
        """
        writer.write('%s<dataset id="%s" dimensions="%s">%s' % (indent, self.datasetid, self.dimensions, newl))
        indent2 = addindent + indent
        for l, x, y, d in zip(self.labels, self.frames, self.values, self.durations):
            writer.write('%s<point label="%s" frame="%d" value="%f" duration="%d"/>%s' % (indent2, self.int2label[l], x, y, d, newl))
        writer.write('%s</dataset>%s' % (indent, newl))
