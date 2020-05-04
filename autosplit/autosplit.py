#!/usr/bin/env python
# coding: utf-8
""" Usage:
    python3 autosplit.py [wavfile]
    
    This program takes a wav file, and based on the corresponding 
	.srt file, split the wav into roughly 30 seconds segement and 
	generate its corresponding .txt file
"""
import pysrt
import srt
import os
import sys

def autosplit(inf):
	INWAV = inf
	INFN = INWAV[:-4]+".srt"
	TMPFN = "_tmp.srt"

	# This section parse the srt file and make it legal
	with open(INFN, 'r', encoding = 'UTF-8') as file:
		try:
			data = file.read()
		except:
			print(INFN, "open error")
			sys.exit()
	
	subtitle_generator = srt.parse(data)
	subtitles = list(subtitle_generator)
        
	txtf = open(TMPFN, "w", encoding="UTF-8") 
	txtf.write(srt.compose(subtitles)) 
	txtf.close() #to cha

	#This section handle the correct .srt files
	subs = pysrt.open(TMPFN)

	idx = 0
	startt = subs[0].start
	subtext = ""
	for ls in range(len(subs)):
		s = subs[ls]
		subtext = subtext + s.text + " "
		tdiff = s.end.__sub__(startt)
		#print(ls, s, tdiff)
		if tdiff.seconds > 30 or ls == len(subs) - 1:
			print("-------")
			#tstart = startt.minutes * 60 + startt.seconds + startt.milliseconds / 1000.
			tstart = str(startt.hours)+":"+str(startt.minutes) + ":" + str('{:02d}'.format(startt.seconds)) + "."+ str(startt.milliseconds)
			tend = tdiff.minutes * 60 + tdiff.seconds + tdiff.milliseconds / 1000.
			outwavf = INWAV[:-4]+"-"+str('{:02d}'.format(idx))+".wav"
			cmd = "sox "+ INWAV + " " + outwavf + " trim " + tstart + " " + str(tend)
			print(cmd)
			os.system(cmd)
			
			# Handle textfile
			txtfn = outwavf[:-4]+".txt"
			txtf = open(txtfn,"w",encoding="UTF-8") 
			print(txtfn, subtext)
			txtf.write(subtext) 
			txtf.close() #to change file access modes 

			#increase 
			idx = idx + 1
			subtext = ""
			
			if ls < len(subs) - 1:
				startt = subs[ls+1].start
			else:
				startt = subs[ls].end

def main():
    if (len(sys.argv) != 2):
        print(__doc__)
        sys.exit(-1)
    else:
        wavf = sys.argv[1]
        autosplit(wavf)

if __name__ == "__main__":
    main()

