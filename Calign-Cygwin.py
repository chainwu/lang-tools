#!/usr/bin/env python3
#-*- coding: utf-8 -*-
""" Usage:
      Calign.py [options] wavfile trsfile output_file
      where options may include:
          -r sampling_rate -- override which sampling rate model to use, either 8000 or 16000
          -a user_supplied_dictionary -- encoded in utf8, the dictionary will be combined with the dictionary in the model
          -d user_supplied_dictionary -- encoded in utf8, the dictionary will be used alone, NOT combined with the dictionary in the model
          -p punctuations -- encoded in utf8, punctuations and other symbols in this file will be deleted in forced alignment, the default is to use "puncs" in the model 
"""

import os
import sys
import getopt
import wave
import codecs
import io
import tempfile
import subprocess
from opencc import OpenCC
from ast import literal_eval
from subprocess import check_output

#HOMEDIR = '/Users/phoneticslabnccu/Documents/P2f/Forced_Aligner_Mandarin'
HOMEDIR='.'
MODEL_DIR = HOMEDIR + '/model'

def prep_mlf(trsfile, tmpbase):

    f = codecs.open(tmpbase + '.dict', 'r', 'utf-8')
    lines = f.readlines()
    f.close()
    dict = []
    for line in lines:
        dict.append(line.split()[0])
    f = codecs.open(tmpbase + '.puncs', 'r', 'utf-8')
    lines = f.readlines()
    f.close()
    puncs = []
    for line in lines:
        puncs.append(line.strip())

    f = codecs.open(trsfile, 'r', 'utf-8')
    lines = f.readlines()
    f.close()

    fw = codecs.open(tmpbase + '.mlf', 'w', 'utf-8')
    fw.write('#!MLF!#\n')
    fw.write('"' + tmpbase + '.lab"\n')
    fw.write('sp\n')
    i = 0
    unks = set()
    while (i < len(lines)):
        txt = lines[i].replace('\n', '')
        txt = txt.replace('{breath}', 'br').replace('{noise}', 'ns')
        txt = txt.replace('{laugh}', 'lg').replace('{laughter}', 'lg')
        txt = txt.replace('{cough}', 'cg').replace('{lipsmack}', 'ls')
        for pun in puncs:
            txt = txt.replace(pun,  '')
        for wrd in txt.split():
            if (wrd in dict):
                fw.write(wrd + '\n')
                fw.write('sp\n')
            else:
                unks.add(wrd)
        i += 1
    fw.write('.\n')
    fw.close()
    return unks


def gen_res(infile1, infile2, outfile):
    
    f = codecs.open(infile1, 'r', 'utf-8')
    lines = f.readlines()
    f.close()
    
    f = codecs.open(infile2, 'r', 'utf-8')
    lines2 = f.readlines()
    f.close()
    words = []
    for line in lines2[2:-1]:
        if (line.strip() != 'sp'):
            words.append(line.strip())
    words.reverse()

    fw = codecs.open(outfile, 'w', 'utf-8')
    fw.write(lines[0])
    fw.write(lines[1])
    for line in lines[2:-1]:
        if ((line.split()[-1].strip() == 'sp') or (len(line.split()) != 5)):
            fw.write(line)
        else:
            fw.write(line.split()[0] + ' ' + line.split()[1] + ' ' + line.split()[2] + ' ' + line.split()[3] + ' ' + words.pop() + '\n')
    fw.write(lines[-1])

def getopt2(name, opts, default = None) :
        value = [v for n,v in opts if n==name]
        if len(value) == 0 :
                return default
        return value[0]

################# Added by lihsin #######################
def readAlignedMLF(mlffile, SR, wave_start):
    # This reads a MLFalignment output  file with phone and word
    # alignments and returns a list of words, each word is a list containing
    # the word label followed by the phones, each phone is a tuple
    # (phone, start_time, end_time) with times in seconds.
    #print("mlffile", mlffile)
    f = open(mlffile, 'r')
    lines = [l.rstrip() for l in f.readlines()]
    f.close()
        
    if len(lines) < 3 :
        raise ValueError("Alignment did not complete succesfully.")
        
    j = 2
    ret = []
    while (lines[j] != '.'):
        if (len(lines[j].split()) == 5): # Is this the start of a word; do we have a word label?
            # Make a new word list in ret and put the word label at the beginning
            wrd = lines[j].split()[4]
            ret.append([wrd])
            
        # Append this phone to the latest word (sub-)list
        ph = lines[j].split()[2]
        if (SR == 11025):
            st = (float(lines[j].split()[0])/10000000.0 + 0.0125)*(11000.0/11025.0)
            en = (float(lines[j].split()[1])/10000000.0 + 0.0125)*(11000.0/11025.0)
        else:
            st = float(lines[j].split()[0])/10000000.0 + 0.0125
            en = float(lines[j].split()[1])/10000000.0 + 0.0125
        if st < en:
            ret[-1].append([ph, st+wave_start, en+wave_start])
                
        j += 1
                    
    return ret

def writeTextGrid(outfile, word_alignments) :
    # make the list of just phone alignments
    cc = OpenCC('s2t')
    phons = []
    for wrd in word_alignments :
        phons.extend(wrd[1:]) # skip the word label
    
    # make the list of just word alignments
    # we're getting elements of the form:
    #   ["word label", ["phone1", start, end], ["phone2", start, end], ...]
    wrds = []
    for wrd in word_alignments :
        # If no phones make up this word, then it was an optional word
        # like a pause that wasn't actually realized.
        if len(wrd) == 1 :
            continue
        wrds.append([wrd[0], wrd[1][1], wrd[-1][2]]) # word label, first phone start time, last phone end time
        
    #write the phone interval tier
    #fw = open(outfile, 'w')
    fw = codecs.open(outfile, "w", "utf-8")
    fw.write('File type = "ooTextFile short"\n')
    fw.write('"TextGrid"\n')
    fw.write('\n')
    fw.write(str(phons[0][1]) + '\n')
    fw.write(str(phons[-1][2]) + '\n')
    fw.write('<exists>\n')
    fw.write('2\n')
    fw.write('"IntervalTier"\n')
    fw.write('"phone"\n')
    fw.write(str(phons[0][1]) + '\n')
    fw.write(str(phons[-1][-1]) + '\n')
    fw.write(str(len(phons)) + '\n')
    for k in range(len(phons)):
        fw.write(str(phons[k][1]) + '\n')
        fw.write(str(phons[k][2]) + '\n')
        fw.write('"' + phons[k][0] + '"' + '\n')

    #write the word interval tier
    fw.write('"IntervalTier"\n')
    fw.write('"word"\n')
    fw.write(str(phons[0][1]) + '\n')
    fw.write(str(phons[-1][-1]) + '\n')
    fw.write(str(len(wrds)) + '\n')
    for k in range(len(wrds) - 1):
        fw.write(str(wrds[k][1]) + '\n')
        fw.write(str(wrds[k+1][1]) + '\n')
        #print(">>>", len(wrds[k][0].encode('utf-8')))
        #fw.write('"' + str(wrds[k][0].encode('utf-8').decode('utf-8')) + '"' + '\n')
        utf8str= literal_eval("b'{}'".format(wrds[k][0])).decode('utf-8')
        tutf8str = cc.convert(utf8str)
        fw.write('"' + tutf8str + '"' + '\n')
        #fw.write('"' + wrds[k][0] + '"' + '\n')
        
    fw.write(str(wrds[-1][1]) + '\n')
    fw.write(str(phons[-1][2]) + '\n')
    fw.write('"' + wrds[-1][0] + '"' + '\n')
        
    fw.close()

##################################################

if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], "r:a:d:p:")

        # get the three mandatory arguments
        wavfile, trsfile, outfile = args
        missing = io.open(wavfile[:-4]+'.MissingWords', 'w', encoding='utf8')
        # get options
        sr_override = getopt2("-r", opts)
        wave_start = getopt2("-s", opts, "0.0")
        wave_end = getopt2("-e", opts, None)
        dict_add = getopt2("-a", opts)
        dict_alone = getopt2("-d", opts)
        puncs = getopt2("-p", opts)

    except:
        print(__doc__)
        sys.exit(0)

    #tmpbase = '/tmp/' + os.environ['USER'] + '_' + str(os.getpid())
    #temp_folder = tempfile.gettempdir()
    temp_folder = 'C:/Users/'+os.getlogin()+'/AppData/Local/Temp'
    print("temp_folder = ",temp_folder)
    temp_file = os.getlogin() + '_' + str(os.getpid())
    TMPBASE = os.path.join(temp_folder, temp_file)
    tmpbase = TMPBASE
    
    #find sampling rate and prepare wavefile
    if sr_override:
        SR = int(sr_override)
        os.system('sox ' + wavfile + ' -r ' + str(SR) + ' -S ' + tmpbase + '.wav')
    else:
        f = wave.open(wavfile, 'r')
        SR = f.getframerate()
        f.close()
        if (SR not in [8000, 16000]):
            print('sox ' + wavfile + ' -r 16000 ' + tmpbase + '.wav')
            os.system('sox ' + wavfile + ' -r 16000 -S ' + tmpbase + '.wav')
            SR = 16000
        else:
            os.system('cp -f ' + wavfile + ' ' + tmpbase + '.wav') 
 
    #prepare plpfile
    print('../HTK/HCopy -C ' + MODEL_DIR + '/' + str(SR) + '/config ' + tmpbase + '.wav ' + tmpbase + '.plp')
    os.system('../HTK/HCopy -C ' + MODEL_DIR + '/' + str(SR) + '/config ' + tmpbase + '.wav ' + tmpbase + '.plp')

    #prepare mlfile and dictionary
    if dict_alone:
        f = codecs.open(dict_alone, 'r', 'utf-8')
        lines = f.readlines()
        f.close()
        lines = lines + ['sp sp\n']
    else:
        #print("dict not alone:", MODEL_DIR+'/dict')
        f = codecs.open(MODEL_DIR + '/dict', 'r', 'utf-8')
        lines = f.readlines()
        #print(lines)
        f.close()
        if (dict_add):
            f = codecs.open(dict_add, 'r', 'utf-8')
            lines2 = f.readlines()
            f.close()
            lines = lines+lines2
            print(lines2)
    fw = codecs.open(tmpbase + '.dict', 'w', 'utf-8')
    for line in lines:
        #print(line)
        fw.write(line)

    if puncs:
        os.system('cp -f ' + puncs + ' ' + tmpbase + '.puncs')
    else:
        os.system('cp -f ' + MODEL_DIR + '/puncs ' + tmpbase + '.puncs') 

    unks = prep_mlf(trsfile, tmpbase)
    for unk in unks:
        missing.write(u'Missing: ' + unk + '\n')
    
    #run alignment
    print('../HTK/HVite -A -T 1 -a -m -t 10000.0 10000.0 100000.0 -I ' + tmpbase + '.mlf -H ' + MODEL_DIR + '/' + str(SR) + '/macros -H ' + MODEL_DIR + '/' + str(SR) + '/hmmdefs -i ' + tmpbase + '.aligned' + ' ' + MODEL_DIR + '/dict ' + MODEL_DIR + '/monophones ' + tmpbase + '.plp')
    os.system('../HTK/HVite -A  -T 1 -a -m -t 10000.0 10000.0 100000.0 -I ' + tmpbase + '.mlf -H ' + MODEL_DIR + '/' + str(SR) + '/macros -H ' + MODEL_DIR + '/' + str(SR) + '/hmmdefs -i ' + tmpbase + '.aligned' + ' ' + MODEL_DIR + '/dict ' + MODEL_DIR + '/monophones ' + tmpbase + '.plp')
    #HVITECONVCMD = '../HTK/HVite -A  -T 1 -a -m -t 10000.0 10000.0 100000.0 -I ' + tmpbase + '.mlf -H ' + MODEL_DIR + '/' + str(SR) + '/macros -H ' + MODEL_DIR + '/' + str(SR) + '/hmmdefs -i ' + tmpbase + '.aligned' + ' ' + tmpbase + '.dict ' + MODEL_DIR + '/monophones ' + tmpbase + '.plp'
    #try:
    #    out_bytes = check_output(HVITECONVCMD, shell = True)
    #except subprocess.CalledProcessError as e:
    #    out_bytes = e.output       # Output generated before error
    #    code = e.returncode   # Return code	
    #print(out_bytes)
	
    #Uncomment this one if you need the original version
    #gen_res(tmpbase + '.aligned', tmpbase + '.mlf', outfile)


    # output the alignment as a Praat TextGrid: TextGrid('./tmp/aligned.mlf', outfile, SR)
    writeTextGrid(outfile, readAlignedMLF(tmpbase + '.aligned', SR, float(wave_start)))

    #clean up
    os.system('rm -f ' + tmpbase + '*')
