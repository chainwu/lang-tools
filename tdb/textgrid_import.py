#!/usr/bin/env python3
#-*- coding: utf-8 -*-
""" Usage:
    textgrid_import.py wav_file textgrid_file 

    This script will import a wav file and a textgrid file into MySQL database
"""

import tgt
import os
import glob
import configparser
import mysql.connector
from shutil import copyfile
import sys

MEDIAPATH='/opt/textgrid/'

def MySQL_Connect():
    config = configparser.ConfigParser()
    config.read('config.ini')
    cnx = mysql.connector.connect(user=config['mysqlDB']['user'], 
                                  password=config['mysqlDB']['pass'],
                                  host=config['mysqlDB']['host'],
                                  database=config['mysqlDB']['db'])
    return cnx

def mysql_file_table(cnx, tgtfn, wavfn):
    copyfile(tgtfn,MEDIAPATH+tgtfn)
    copyfile(wavfn,MEDIAPATH+wavfn)

    tg = tgt.io.read_textgrid(tgtfn)
    tier_name = tg.get_tier_names()
    cursor = cnx.cursor()
    add_files = ("INSERT INTO file_table (txtgrid, wav, total_tier, start_time, end_time) VALUES (%s, %s, %s, %s, %s)")
    data_files = (tgtfn, wavfn, len(tier_name), tg.start_time, tg.end_time)
    cursor.execute(add_files, data_files)
    cnx.commit()
    return tg, cursor.lastrowid

def mysql_tier_table(cnx, tg, fid):
    tiers = tg.get_tier_names()
    sid = 0
    for t in tiers:
        tr = tg.get_tier_by_name(t)
        cursor = cnx.cursor()
        add_files = ("INSERT INTO tier_table (file_id, seq_id, tier_name, tier_type, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s)")
        data_files = (fid, sid, t, tr.tier_type(), tr.start_time, tr.end_time)
        cursor.execute(add_files, data_files)
        sid = sid + 1
        cnx.commit()
        tid = cursor.lastrowid

        asid = 0
        for a in tr._objects:
            cursor = cnx.cursor()
            add_files = ("INSERT INTO annotation_table (text, tier_id, seq_id, start_time, end_time) VALUES (%s, %s, %s, %s, %s)")
            data_files = (a.text, tid, asid, a.start_time, a.end_time)
            asid = asid + 1
            cursor.execute(add_files, data_files)
            cnx.commit()
            
        
if __name__ == '__main__':
    # get the three mandatory arguments
    wavfile, tgfile = sys.argv[1:]
    
    cnx = MySQL_Connect()
    tg, fid = mysql_file_table(cnx, tgfile, wavfile)
    mysql_tier_table(cnx, tg, fid)
    cnx.close()    
    
#except Exception as e:
    #print(__doc__)
#    print(e)
#    sys.exit(-1)
#cnx.close()
