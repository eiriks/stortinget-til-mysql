#!/usr/bin/env python
# encoding: utf-8


# ===================================================================
# = her leker jeg med å nøste ut data fra et fylkesperspektiv. wip. =
# ===================================================================

import sys
import os
#import requests         # http://kennethreitz.com/requests-python-http-module.html
#import json
#import time
#from bs4 import BeautifulSoup
#import xml.etree.cElementTree as et
import MySQLdb
conn = MySQLdb.connect(host = "localhost", user = "root", passwd = "root", db = "stortinget", charset='utf8') # dette må du naturlig nok tilpasse din egen maskin..


def dagens_representanter_for(fylke_id):
    cursor = conn.cursor() 
    cursor.execute("""SELECT * FROM dagensrepresentanter WHERE fylke = '%s' """ % (fylke_id))
    #cursor.execute("""SELECT * FROM dagensrepresentanter """)
    #cursor.execute("""SELECT * FROM dagensrepresentanter WHERE fylke = 'AA' """)
    print "%s rows fetched" % cursor.rowcount
    #print len(cursor.fetchall())
    
    for rep in cursor.fetchall(): 
        print rep
        cursor.execute("""SELECT * FROM allekomiteer k, dagensrepresentanter_komiteer d WHERE k.id = d.kom_id AND d.rep_id = '%s' """ % (rep[0]))
        for kom in cursor.fetchall():
            print "\t", kom
    cursor.close()
    conn.close()
    #conn.commit()
    
    

def representanter(fylke_id):
    cursor = conn.cursor() 
    #cursor.executemany(""" insert IGNORE into table (versjon, fra, id, til) values (%s, %s, %s, %s)""", perioder)
    cursor.execute("""SELECT * FROM `representanter` WHERE `fylke_id` = '%s' ORDER BY `stortingsperiodeid` DESC""" % (fylke_id))
    print "%s row fetched" % cursor.rowcount
    for rep in cursor.fetchall(): 
        print rep
    




def main():
    #print representanter('AA')
    print dagens_representanter_for('AA')



if __name__ == '__main__':
	main()

