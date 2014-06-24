import my_minidom as XML
from bz2 import BZ2File
from os.path import basename
import wave
from xmlutils.getElementsByTagList import getElementsByTagList
import numpy as N

from continuousdataset import ContinuousDataset

class SVEnv:
    @classmethod
    def parse(cls, fname):
        f = BZ2File(fname, 'r')
        return XML.parse(f)

    def __namefact(self, name):
        if name not in self.__dname:
            self.__dname[name] = 0
            return name
        self.__dname[name] += 1
        return 'name <%d>' % self.__dname[name]

    def __init__(self, wavpath, showspectro=False):
        imp = XML.getDOMImplementation()
        #dt = imp.createDocumentType('dt1', 'dt2', 'dt3')
        dt = imp.createDocumentType('sonic-visualiser', None, None)
        self.doc = doc = imp.createDocument(None,'sv', dt)
        root = doc.documentElement
        self.__dname = dict()
        self.showspectro = showspectro

        self.data = root.appendChild(doc.createElement('data'))
        self.display = root.appendChild(doc.createElement('display'))
        window = self.display.appendChild(doc.createElement('window'))
        self.defwidth = 900
        window.setAttribute('width', str(self.defwidth))
        window.setAttribute('height', str(856))
        self.selections = root.appendChild(doc.createElement('selections'))


        self.nbdata = 0
        self.__addWaveModel(wavpath)

        ### add layers!!!
        
        # add views      

        # pxml = doc.toprettyxml()
        # print pxml

    def __add_view(self, height=177):
        view = self.display.appendChild(self.doc.createElement('view'))
        view.setAttribute('centre', str(self.nframes / 2))
        view.setAttribute('zoom', str(2048))#str(self.nframes / self.defwidth))
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
        assert(w.getnchannels() == 1)
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
        if self.showspectro:
            spectrolayer = self.__add_spectrogram(0)
            spectroruler = self.__add_time_ruler()

        view = self.__add_view()
        self.__add_layer_reference(view, wavetimeruler)
        self.__add_layer_reference(view, wavelayer)

        if self.showspectro:
            view = self.__add_view()
            self.__add_layer_reference(view, spectroruler)
            self.__add_layer_reference(view, spectrolayer)


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

    def add_continuous_annotations(self, x, y, colourName='Purple', colour='#c832ff', name='', view=None, vscale=None):
        samplerate = 16000
        model = self.data.appendChild(self.doc.createElement('model'))
        imodel = self.nbdata
        
        for atname, atval in [('id', imodel + 1),
                              ('dataset', imodel),
                              ('name', name),
                              ('sampleRate', samplerate),
                              ('start', int(min(x) * samplerate)),
                              ('end', int(max(x) * samplerate)),
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
        
        data = dataset.appendChild(self.doc.createTextNode(''))
        data.data = ContinuousDataset(map(int, N.array(x) * samplerate), y)
        print data.data, data.data.__class__
        #exit(42)
        # for xval, yval in zip(x,y):
        #     point = dataset.appendChild(self.doc.createElement('point'))
        #     point.setAttribute('label', 'New Point')
        #     point.setAttribute('frame', int(xval * samplerate))
        #     point.setAttribute('value', yval)


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

        ###### add views
        if view is None:
            view = self.__add_view()
        self.__add_layer_reference(view, valruler)
        #view = self.__add_view()
        self.__add_layer_reference(view, vallayer)
        return view
            

    def save(self, outfname):       
        f = BZ2File(outfname, 'w')
        self.doc.writexml(f)
        f.close()
        

    def add_transcriber_layer(self, fname):

        samplerate = 16000
        colourName='Purple'
        colour='#c832ff'

        ldatasets = []
        lmodels = []

        for modelname in ['transcription', 'speaker', 'overlap']:
            model = self.data.appendChild(self.doc.createElement('model'))
            lmodels.append(model)
            imodel = self.nbdata
            for atname, atval in [('id', imodel + 1),
                                  ('dataset', imodel),
                                  ('name', modelname),
                                  ('sampleRate', samplerate),
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
            ldatasets.append(dataset)
            dataset.setAttribute('id', str(imodel))
            dataset.setAttribute('dimensions', '3')
            self.nbdata += 2
        
            # add layers
            valruler = self.__add_time_ruler()
            vallayer = self.__add_region_layer(imodel + 1, modelname)
            vallayer.setAttribute('colourName', colourName)
            vallayer.setAttribute('colour', colour)

            ###### add views
            if modelname == 'transcription':
                view = self.__add_view(height='50')
            else:
                view = self.__add_view()
            self.__add_layer_reference(view, valruler)
            self.__add_layer_reference(view, vallayer)


        doc = XML.parse(fname)
        assert(len(doc.getElementsByTagName('Episode')) == 1)
        for sec in doc.getElementsByTagName('Section'):
            sectype = sec.getAttribute('type')
            assert(sectype in ['report', 'nontrans'])
            if sectype != 'report':
                continue
            point = ldatasets[0].appendChild(self.doc.createElement('point'))
            point.setAttribute('label', 'report')
            framestart = int(float(sec.getAttribute('startTime')) * samplerate)
            framedur = int(float(sec.getAttribute('endTime')) * samplerate) - framestart
            point.setAttribute('frame', str(framestart))
            point.setAttribute('duration', str(framedur))
            point.setAttribute('value', '0')

            for turn in sec.getElementsByTagName('Turn'):
                assert(turn.hasAttribute('startTime'))
                assert(turn.hasAttribute('endTime'))
                if turn.hasAttribute('speaker'):
                    assert(turn.attributes.length == 3)
                    point = ldatasets[1].appendChild(self.doc.createElement('point'))
                    point.setAttribute('label', 'speaker')
                    framestart = int(float(turn.getAttribute('startTime')) * samplerate)
                    framedur = int(float(turn.getAttribute('endTime')) * samplerate) - framestart
                    point.setAttribute('frame', str(framestart))
                    point.setAttribute('duration', str(framedur))
                    point.setAttribute('value', turn.getAttribute('speaker')[3:])

                    #print 'nboverlap', len(turn.getElementsByTagName('Overlap'))
                    overlaps = self.__detectoverlaps(turn, getElementsByTagList(turn, ['Overlap', 'Sync']))
                    for ovbeg, ovend, ovspkr in overlaps:
                        point = ldatasets[2].appendChild(self.doc.createElement('point'))
                        point.setAttribute('label', 'ovspeaker')
                        framestart = int(float(turn.getAttribute('startTime')) * samplerate)
                        framedur = int(float(turn.getAttribute('endTime')) * samplerate) - framestart
                        point.setAttribute('frame', str(framestart))
                        point.setAttribute('duration', str(framedur))
                        point.setAttribute('value', turn.getAttribute('speaker')[3:])
                else:
                    assert(turn.attributes.length == 2)
                    

        for i in xrange(3):
            model = lmodels[i]
            dataset = ldatasets[i]
            #print 'i', i
            lpoints = dataset.getElementsByTagName('point')
            #print lpoints
            model.setAttribute('start', lpoints[0].getAttribute('frame'))
            model.setAttribute('end', lpoints[-1].getAttribute('frame'))
            lvals = [int(p.getAttribute('value')) for p in lpoints]
            model.setAttribute('minimum', str(min(lvals)))
            model.setAttribute('maximum', str(max(lvals)))


    def __detectoverlaps(self, turn, ovlist):
        while ovlist and ovlist[0].nodeName == 'Sync':
            begin = ovlist.pop(0).getAttribute('time')
        if len(ovlist) == 0:
            return []
        primovopen = ovlist.pop(0)
        primovclose = ovlist.pop(0)
        assert(primovopen.getAttribute('type') == 'primary')
        assert(primovclose.getAttribute('type') == 'primary')
        assert(primovopen.getAttribute('extent') == 'begin')
        assert(primovclose.getAttribute('extent') == 'end')
        #print 'begin', begin

        if len(ovlist) > 0 and ovlist[0].nodeName == 'Overlap':
            backopen = ovlist.pop(0)
            backclose = ovlist.pop(0)
            assert(backopen.getAttribute('type') == 'backchannel')
            assert(backclose.getAttribute('type') == 'backchannel')
            assert(backopen.getAttribute('extent') == 'begin')
            assert(backclose.getAttribute('extent') == 'end')
            spkr = backopen.getAttribute('speaker')
        else:
            # FIXME: spk -1 may be an annotation error
            spkr = 'spk-1'

        if len(ovlist) == 0:
            end = turn.getAttribute('endTime')
        elif ovlist[0].nodeName == 'Sync':
            end = ovlist[0].getAttribute('time')
        else:
            raise NotImplementedError('Several backchannel overlaps')
        ret = [(begin, end, spkr)]
        ret.extend(self.__detectoverlaps(turn, ovlist))
        return ret


if __name__ == '__main__':
    import numpy as N
    fname = '/vol/homedir/doukhan/svtest/testSS.sv'
    #doc = SVEnv.parse(fname)
    #print doc.toprettyxml()
    t = SVEnv('/vol/homedir/doukhan/BFMTV_BFMStory_2010-09-03_175900.wav')
    x = N.array(range(10000, 20000, 5)) / 1000.
    t.add_continuous_annotations(x, 1 + 3 * N.sin(2 * x))

    


    transfname = '/home/doukhan/etape/ref/trn2/BFMTV_BFMStory_2010-09-03_175900.trs'
    
    t.add_transcriber_layer(transfname)


    # print t.doc.toprettyxml()

    t.save('/home/doukhan/test.sv')
