import sys
from py_sonicvisualiser import SVEnv

wavfname = sys.argv[1]
outsvenvname = sys.argv[2]

# init a sonic visualiser environment file corresponding
# to the analysis of media wavfname
sve = SVEnv(wavfname)

# add a spectrogram view
sve.add_spectrogram()

# append a continuous annotation layer corresponding to a sinusoidal signal
x = np.array(range(10000, 20000, 5)) / 1000.
ca = t.add_continuous_annotations(x, 1 + 3 * np.sin(2 * x))

# add a spectrogram in the same view than the sinusoidal continuous annotation
t.add_spectrogram(view=ca)

# append a labelled interval annotation layer
intvtime = [1., 5., 21.5]
intvdur = [3., 11., 5.]
intvlabel = ['myintv1', 'mywonderfull  intv2', 'intv3']
intvval = [0, 1, 5]
t.add_interval_annotations(intvtime,intvdur,intvlabel,intvval)

# save the environment to a sonic visualiser environment file
t.save(outsvenvfname)
