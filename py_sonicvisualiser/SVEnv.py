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
This class allows to generate a sonicvisualiser environment file
consisting of a reference to a wav audio sound file, and several
annotation layers
"""

import xml.dom.minidom as xml
from bz2 import BZ2File
from os.path import basename
import wave
import numpy as np
from continuous_dataset_node import ContinuousDatasetNode


class SVEnv:
    """
    This class allows to generate sonic visualiser environment files
    """

    def __init__(self, wavpath):
        """
        Init a sonic visualiser environment structure
        
        :param wavpath: Full path to the wav file used in the current environment
        :type wavpath: string
        """
        imp = xml.getDOMImplementation()
        dt = imp.createDocumentType('sonic-visualiser', None, None)
        self.doc = doc = imp.createDocument(None,'sv', dt)
        root = doc.documentElement
        self.__dname = dict()

        self.data = root.appendChild(doc.createElement('data'))
        self.display = root.appendChild(doc.createElement('display'))
        window = self.display.appendChild(doc.createElement('window'))
        self.defwidth = 900
        window.setAttribute('width', str(self.defwidth))
        window.setAttribute('height', str(856))
        self.selections = root.appendChild(doc.createElement('selections'))


        self.nbdata = 0
        self.__addWaveModel(wavpath)


    def add_spectrogram(self, view=None):
        """
        add a spectrogram layer to the environment

        :param view: environment view used to display the spectrogram, if set to None, a new view is created
        :type view: <DOM Element: view>
        : returns: the view used to store the spectrogram
        : rtype: <DOM Element: view>
        """
        spectrolayer = self.__add_spectrogram(0)
        spectroruler = self.__add_time_ruler()
        if view is None:
            view = self.__add_view()
        self.__add_layer_reference(view, spectroruler)
        self.__add_layer_reference(view, spectrolayer)
        return view



    def add_continuous_annotations(self, x, y, colourName='Purple', colour='#c832ff', name='', view=None, vscale=None):
        """
        add a continous annotation layer

        :param x: The temporal indices of the dataset
        :param y: The values of the dataset
        :param view: environment view used to display the spectrogram, if set to None, a new view is created
        :type x: iterable
        :type y: iterable
        :type view: <DOM Element: view>
        : returns: the view used to store the spectrogram
        : rtype: <DOM Element: view>
        """
        
        model = self.data.appendChild(self.doc.createElement('model'))
        imodel = self.nbdata
        
        for atname, atval in [('id', imodel + 1),
                              ('dataset', imodel),
                              ('name', name),
                              ('sampleRate', self.samplerate),
                              ('start', int(min(x) * self.samplerate)),
                              ('end', int(max(x) * self.samplerate)),
                              ('type', 'sparse'),
                              ('dimensions', '2'),
                              ('resolution', '1'),
                              ('notifyOnAdd', 'true'),
                              ('minimum', min(y)),
                              ('maximum', max(y)),
                              ('units', '')
                              ]:
            model.setAttribute(atname, str(atval))

        dataset = self.data.appendChild(self.doc.createElement('dataset'))
        dataset.setAttribute('id', str(imodel))
        dataset.setAttribute('dimensions', '2')
        self.nbdata += 2
        
        data = dataset.appendChild(ContinuousDatasetNode.create(self.doc, map(int, np.array(x) * self.samplerate), y))

        ###### add layers
        valruler = self.__add_time_ruler()
        vallayer = self.__add_val_layer(imodel + 1)
        vallayer.setAttribute('colourName', colourName)
        vallayer.setAttribute('colour', colour)
        if vscale is None:
            vallayer.setAttribute('verticalScale', '0')
            vallayer.setAttribute('scaleMinimum', str(min(y)))
            vallayer.setAttribute('scaleMaximum', str(max(y)))
        else:
            vallayer.setAttribute('verticalScale', '0')
            vallayer.setAttribute('scaleMinimum', str(vscale[0]))
            vallayer.setAttribute('scaleMaximum', str(vscale[1]))

        if view is None:
            view = self.__add_view()
        self.__add_layer_reference(view, valruler)
        self.__add_layer_reference(view, vallayer)
        return view


    def add_interval_annotations(self, temp_idx, durations, labels, values=None, colourName='Purple', colour='#c832ff', name='', view=None):
        """
        add a labelled interval annotation layer

        :param temp_idx: The temporal indices of the invervals beginning (sec)
        :param durations: intervals durations
        :param labels: interval labels
        :param values: interval numeric values, if set to None, values are set to 0
        :param view: environment view used to display the spectrogram, if set to None, a new view is created

        :type temp_idx: float container
        :type durations: float container
        :type labels: string contained
        :type values: int container
        :type view: <DOM Element: view>

        : returns: the view used to store the interval annotation layer
        : rtype: <DOM Element: view>
        """
        model = self.data.appendChild(self.doc.createElement('model'))
        imodel = self.nbdata
        for atname, atval in [('id', imodel + 1),
                              ('dataset', imodel),
                              ('name', name),
                              ('sampleRate', self.samplerate),
                              ('type', 'sparse'),
                              ('dimensions', '3'),
                              ('subtype', 'region'),
                              ('resolution', '1'),
                              ('notifyOnAdd', 'true'),
                              ('units', ''),
                              ('valueQuantization', '0')
                              ]:
            model.setAttribute(atname, str(atval))

        dataset = self.data.appendChild(self.doc.createElement('dataset'))
        dataset.setAttribute('id', str(imodel))
        dataset.setAttribute('dimensions', '3')
        self.nbdata += 2
        
        valruler = self.__add_time_ruler()
        vallayer = self.__add_region_layer(imodel + 1, name)
        vallayer.setAttribute('colourName', colourName)
        vallayer.setAttribute('colour', colour)
        
        if view is None:
            view = self.__add_view()
        self.__add_layer_reference(view, valruler)
        self.__add_layer_reference(view, vallayer)

        if values is None:
            values = ([0] * len(temp_idx))
        for t, d, l, v in zip(temp_idx, durations, labels, values):
            point = dataset.appendChild(self.doc.createElement('point'))
            point.setAttribute('label', l)
            point.setAttribute('frame', str(int(t * self.samplerate)))
            point.setAttribute('duration', str(int(d * self.samplerate)))
            point.setAttribute('value', str(v))
        return view


    def save(self, outfname):
        """
        Save the environment of a sv file to be used with soniv visualiser

        :param outfname: full path to the file storing the environment
        :type outfname: string
        """
        f = BZ2File(outfname, 'w')
        self.doc.writexml(f, addindent='  ', newl='\n')
        f.close()     



    def __namefact(self, name):
        if name not in self.__dname:
            self.__dname[name] = 0
            return name
        self.__dname[name] += 1
        return 'name <%d>' % self.__dname[name]


    def __add_view(self, height=177):
        view = self.display.appendChild(self.doc.createElement('view'))
        view.setAttribute('centre', str(self.nframes / 2))
        view.setAttribute('zoom', str(2048))
        view.setAttribute('followPan', '1')
        view.setAttribute('followZoom', '1')
        view.setAttribute('tracking', 'page')
        view.setAttribute('type', 'pane')
        view.setAttribute('centreLineVisible', '1')
        view.setAttribute('height', '177')
        return view

    def __addWaveModel(self, wavpath):
        wavmodel = self.data.appendChild(self.doc.createElement('model'))
        self.nbdata += 1
        wavmodel.setAttribute('id', '0')
        wavmodel.setAttribute('name', self.__namefact(basename(wavpath)))
        wavmodel.setAttribute('mainModel', 'true')
        wavmodel.setAttribute('type', 'wavefile')
        wavmodel.setAttribute('file', wavpath)
        w = wave.open(wavpath)
        
        self.nchannels = w.getnchannels()

        self.samplerate =  w.getframerate()
        print 'samplerate', self.samplerate
        wavmodel.setAttribute('sampleRate', str(w.getframerate()))
        wavmodel.setAttribute('start', '0')
        self.nframes = w.getnframes()
        wavmodel.setAttribute('end', str(self.nframes))

        # add play parameters
        playparam = self.data.appendChild(self.doc.createElement('playparameters'))
        playparam.setAttribute('mute', 'false')
        playparam.setAttribute('pan', '0')
        playparam.setAttribute('gain', '1')
        playparam.setAttribute('pluginId','')
        playparam.setAttribute('model', '0')

        # add time ruler
        wavetimeruler = self.__add_time_ruler()
        wavelayer = self.__add_waveform(0)

        view = self.__add_view()
        self.__add_layer_reference(view, wavetimeruler)
        self.__add_layer_reference(view, wavelayer)

        


    def __add_layer_reference(self, view, layer):
        layerref = view.appendChild(self.doc.createElement('layer'))
        for at in ['id', 'type', 'name', 'model']:
            layerref.setAttribute(at, layer.getAttribute(at))
        layerref.setAttribute('visible', 'true')


    def __add_layer(self, model, typename):
        layer = self.data.appendChild(self.doc.createElement('layer'))
        layer.setAttribute('id', str(self.nbdata))
        layer.setAttribute('name', self.__namefact(typename + str(self.nbdata)))
        self.nbdata += 1
        layer.setAttribute('model', str(model))
        layer.setAttribute('type', typename)
        return layer

    def __add_val_layer(self, model):
        layer = self.__add_layer(model, 'timevalues')
        layer.setAttribute('plotStyle', '2')
        layer.setAttribute('verticalScale', '0')
        layer.setAttribute('derivative', 'false')
        layer.setAttribute('darkBackground', 'false')
        layer.setAttribute('drawDivisions', 'true')
        layer.setAttribute('colourMap', '0')
        layer.setAttribute('name', self.__namefact('Time Values'))
        return layer


    def __add_region_layer(self, model, modelname):
        layer = self.__add_layer(model, 'regions')
        layer.setAttribute('plotStyle', '0')
        layer.setAttribute('verticalScale', '1')
        layer.setAttribute('darkBackground', 'false')
        layer.setAttribute('name', modelname + 'Region')
        return layer



    def __add_time_ruler(self):
        layer = self.__add_layer(0, 'timeruler')
        layer.setAttribute('colourName', 'Black')
        layer.setAttribute('colour', '#000000')
        layer.setAttribute('darkBackground', 'false')
        return layer

    def __add_waveform(self, model):
        layer = self.__add_layer(model, 'waveform')
        layer.setAttribute('colourName', 'Black')
        layer.setAttribute('colour', '#000000')
        layer.setAttribute('darkBackground', 'false')

        layer.setAttribute('gain', '1')
        layer.setAttribute('showMeans', '1')
        layer.setAttribute('greyscale', '0')
        layer.setAttribute('channelMode', '0')
        layer.setAttribute('channel', '-1')
        layer.setAttribute('scale', '0')
        layer.setAttribute('aggressive', '0')
        layer.setAttribute('autoNormalize', '0')
        return layer
    
    def __add_spectrogram(self, model):
        layer = self.__add_layer(model, 'spectrogram')
        layer.setAttribute('gain', '1')
        layer.setAttribute('channel', '-1')
        layer.setAttribute('windowSize', '1024')
        layer.setAttribute('windowHopLevel', '2')
        layer.setAttribute('threshold', '0')
        layer.setAttribute('minFrequency', '0')
        layer.setAttribute('maxFrequency', '8000')
        layer.setAttribute('colourScale' , '3')
        layer.setAttribute('colourScheme', '0')
        layer.setAttribute('colourRotation', '0')
        layer.setAttribute('frequencyScale', '0')
        layer.setAttribute('binDisplay', '0')
        layer.setAttribute('normalizeColumns', 'false')
        layer.setAttribute('normalizeVisibleArea', 'false')
        return layer


# if __name__ == '__main__':

#     outfname = '/home/david/test.sv'
#     wavfname = '/home/david/crepe.wav'

#     outfname = '/vol/homedir/doukhan/test.sv'
#     wavfname = '/vol/homedir/doukhan/diadems_plusieursloc.wav'

#     t = SVEnv(wavfname)
#     t.add_spectrogram()

    
#     x = np.array(range(10000, 20000, 5)) / 1000.
#     print x
#     ca = t.add_continuous_annotations(x, 1 + 3 * np.sin(2 * x))
#     print ca
#     t.add_spectrogram(view=ca)
    
#     t.add_interval_annotations([1., 5., 21.5],[3., 11., 5.],['intv1', 'mon super intv2', 'intv3'],[0, 1, 5])

#     t.save(outfname)
