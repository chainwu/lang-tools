#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python3
#-*- coding: utf-8 -*-
""" Usage:
      mfcc directory
      Convert all the .wav file under the directory to MFCC (in numpy array format)
"""


# In[2]:


import librosa, librosa.display
import IPython.display
import matplotlib.pyplot as plt
import numpy as np

def wav2mfcc(fn):
    #plt.rcParams['figure.figsize'] = [20, 5]
    y, fs = librosa.load(fn)

#    plt.figure()
#    plt.subplot(3, 1, 1)
#    librosa.display.waveplot(y, sr=fs)
#    plt.show()

    n_fft = int(fs * 0.01)   # window length: 0.01 s
    hop_length = n_fft // 2  # usually one specifies the hop length as a fraction of the window length
    mfccs = librosa.feature.mfcc(y, sr=fs, n_mfcc=24, hop_length=hop_length, n_fft=n_fft)

#    print(mfccs.shape)

#    librosa.display.specshow(mfccs, sr=fs, x_axis='time', y_axis='hz', hop_length=hop_length, cmap='Greys')
#    plt.show()

    np.save(fn[:-4]+'.mfcc', mfccs, allow_pickle=False)


# In[4]:


import glob
import os.path
import sys

if __name__ == '__main__':
    try:
        wavdir = args
        if os.path.isdir(wavdir):
            wavfl = glob.glob(wavdir+'/*.wav')
            for w in wavfl:
                wav2mfcc(w)
    except:
        print(__doc__)
        sys.exit(0)


# In[ ]:




