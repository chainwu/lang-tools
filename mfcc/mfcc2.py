#!/usr/bin/env python
# coding: utf-8
""" Usage:
      mfcc2 directory
      Convert all the .wav file under the directory to MFCC (in numpy array format)
"""


import numpy as np
import scipy.io.wavfile as wav
from python_speech_features import mfcc

def wav2mfcc(fn):
    (rate,sig) = wav.read(fn)
    mfcc_feat = mfcc(sig,rate)
    mfcc_data= np.swapaxes(mfcc_feat, 0 ,1)
    np.save(fn[:-4]+'.mfcc', mfcc_data, allow_pickle=False)

import glob
import os.path
import sys

if __name__ == '__main__':
    try:
        wavdir = sys.argv[1]
        if os.path.isdir(wavdir):
            wavfl = glob.glob(wavdir+'*.wav')
            for w in wavfl:
                wav2mfcc(w)
    except Exception as e:
        print(e)
        print(__doc__)
        sys.exit(-1)
