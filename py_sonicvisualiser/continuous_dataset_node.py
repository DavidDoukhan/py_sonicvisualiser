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

class ContinuousDatasetNode(xml.dom.minidom.Text):
    """
    This class is aimed at storing large datasets in minidom documents
    datasets are stored as iterable structure (lists, numpy arrays, ...)
    This data is converted to sonic visualiser point nodes at writing time
    This allows to avoid the storage of very large xml trees in RAM,
    and avoid swap 
    """

    def __init__(self, x, y):
        """
        Initialize a continuous dataset structure from iterable parameters

        :param x: The temporal indices of the dataset
        :param y: The values of the dataset
        :type x: iterable
        :type y: iterable
        """
        if not isinstance(x, collections.Iterable):
            raise TypeError, "x node contents must be an iterable"
        if not isinstance(y, collections.Iterable):
            raise TypeError, "y node contents must be an iterable"
        assert(len(x) == len(y))
        self.data = (x, y)

    def writexml(self, writer, indent="", addindent="", newl=""):
        """
        Write the continuous  dataset using sonic visualiser xml conventions
        """
        for x, y in zip(self.data[0], self.data[1]):
            writer.write('%s<point label="New Point" frame="%d" value="%f"/>%s' % (indent, x, y, newl))

    @staticmethod
    def create(doc, x, y):
        t = ContinuousDatasetNode(x, y)
        t.ownerDocument = doc
        return t


# if __name__ == '__main__':
#     import xml.dom.minidom as XML
#     imp = XML.getDOMImplementation()
#     dt = imp.createDocumentType('sonic-visualiser', None, None)
#     doc = imp.createDocument(None,'sv', dt)
#     root = doc.documentElement
#     data = root.appendChild(doc.createElement('data'))
#     print data
#     cdn = ContinuousDatasetNode.create(doc, range(10), range(10, 20))
#     root.appendChild(cdn)
#     doc.writexml(open('/tmp/test.txt', 'w'))
