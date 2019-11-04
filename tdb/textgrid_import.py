#!/usr/bin/env python3

import tgt
import os
import glob
import MYSQLdb
import configparser
import MySQLdb.cursors

config = configparser.ConfigParser()
config.read('config.ini')

def connect():
    return MySQLdb.connect(host = config['mysqlDB']['host'],
                           user = config['mysqlDB']['user'],
                           passwd = config['mysqlDB']['pass'],
                           db = config['mysqlDB']['db'])

def mysql_file_table(tgtfn, wavfn):

def mysql_textgrid_table(tg):

def mysql_tier_table(tg, tier):
    for o in tier._obj:
        mysql_annotation(tg, o)

    
def mysql_annotation_table(tg, ann)
    text = ann.text
    st = ann.start_time
    et = ann.end_time
        
def parse_textgrid(tgtfn):
    tg = tgt.core.read_textgrid(tgtfn)
    tiers = tg.get_tier_names()
    for t in tiers:
        mysql_tier_table(tg, t)
