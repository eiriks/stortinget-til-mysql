#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by Eirik Stavelin on 2012-05-09.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import requests         # http://kennethreitz.com/requests-python-http-module.html
#import json
from bs4 import BeautifulSoup
import xml.etree.cElementTree as et
import MySQLdb
conn = MySQLdb.connect(host = "localhost", user = "root", passwd = "root", db = "stortinget")


def get_stortingsperioder():
    url = "http://data.stortinget.no/eksport/stortingsperioder"
    r = requests.get(url) 
    soup = BeautifulSoup(r.content)
    perioder = []
    for per in soup.find_all('stortingsperiode'):
        perioder.append( (per.versjon.text, per.fra.text, per.id.text, per.til.text) )
    cursor = conn.cursor() #(u'1.0', u'2009-10-01T00:00:00', u'2009-2013', u'2013-09-30T23:59:59')
    cursor.executemany(""" insert IGNORE into stortingsperioder (versjon, fra, id, til) values (%s, %s, %s, %s)""", perioder)
    print "%s row inserted (stortingsperioder)" % cursor.rowcount
    conn.commit()
    
    # update current
    current_id = soup.find('innevaerende_stortingsperiode').id.text
    cursor.execute("""UPDATE stortingsperioder SET er_innevaerende = 1 WHERE id = '%s'""" % (current_id))
    print "%s row updated (er_innevaerende satt)" % cursor.rowcount
    conn.commit()
    
    # check if we are in a new stortingsperiode
    cursor.execute("""SELECT * FROM stortingsperioder WHERE er_innevaerende = 1""")
    results = cursor.fetchall()
    
    for result in results:
        if result[0] != current_id:
            print result
            cursor.execute("""UPDATE stortingsperioder SET er_innevaerende = 0 WHERE id = '%s'""" % (result[0]))
            print "%s row updated (gammel stortingsperiode satt til ikke-aktiv)" % cursor.rowcount
            conn.commit()
    
def get_sesjoner():
    """ get topics from..."""
    url = "http://data.stortinget.no/eksport/sesjoner"
    r = requests.get(url) 
    soup = BeautifulSoup(r.content)
    sessions = []
    for se in soup.find_all('sesjon'):
        #print se.versjon.text, se.fra.text, se.id.text, se.til.text
        session = (se.versjon.text, se.fra.text, se.id.text, se.til.text)
        sessions.append(session)
    cursor = conn.cursor() #    1.0 1986-10-01T00:00:00 1986-87 1987-09-30T23:59:59
    cursor.executemany(""" insert IGNORE into sesjoner (versjon, fra, id, til) values (%s, %s, %s, %s)""", sessions)
    print "%s row inserted (sesjoner)" % cursor.rowcount
    conn.commit()

    # insert current
    curren_session_id = soup.find('innevaerende_sesjon').id.text
    cursor.execute("""UPDATE sesjoner SET er_innevaerende = 1 WHERE id = '%s'""" % (curren_session_id))
    print "%s row updated (innevaerende satt)" % cursor.rowcount
    conn.commit()

    # check if we are in a new sessjon
    cursor.execute("""SELECT * FROM sesjoner WHERE er_innevaerende = 1""")
    results = cursor.fetchall()

    #update sessions not longer current. (hopefull just 1, and hopefully just once a year.. )
    for result in results:
        #print result[0], curren_session_id
        if result[0] != curren_session_id:
            print result
            cursor.execute("""UPDATE sesjoner SET er_innevaerende = 0 WHERE id = '%s'""" % (result[0]))
            print "%s row updatert" % cursor.rowcount
            conn.commit()

def get_emner():
    """ get topics from..."""
    url = "http://data.stortinget.no/eksport/emner"
    r = requests.get(url) 
    tree = et.fromstring(r.content)
    
    emne_liste = []
    for node in tree:
        print node.tag, node.text
        # førstenivå: version & emne_liste, sistnevnte kan ittereres:
        for emne in node:
            print "hoved:", emne.tag
            hovedemne = []
            for attribute in emne:
                # alle hovedemner
                print attribute.tag, attribute.text
                
                if attribute.tag != "{http://data.stortinget.no}underemne_liste":
                    hovedemne.append(attribute.text)
                
                #sette av hovedemne IDer slik at undertemaene kan lenkes til hovedemner
                if attribute.tag == "{http://data.stortinget.no}id":
                    hovedemne_id = attribute.text
                
                if attribute.tag == "{http://data.stortinget.no}underemne_liste":
                    # appende hovedtemaer
                    #print hoved_emne #ser bra ut
                    hovedemne.append(0) #er_hovedtema (ja) ingen ID-link
                    emne_liste.append(tuple(hovedemne))
                    hovedemne = []
                    under_emne = []
                    # hvis underemne:liste finnes
                    for subtemanode in attribute:
                        # alle underemner
                        print "\t",subtemanode.tag # aka {http://data.stortinget.no}emne
                        for subtema in subtemanode:
                            # finne subtemaene her: 
                            print "\t\t",subtema.tag, subtema.text
                            if subtema.tag != "{http://data.stortinget.no}underemne_liste":
                                under_emne.append(subtema.text)
                            if subtema.tag == "{http://data.stortinget.no}underemne_liste":
                                under_emne.append(hovedemne_id) #hovedemnet som dette er et undertema for
                                emne_liste.append(tuple(under_emne))
                                under_emne = []
    #print emne_liste
    # print len(emne_liste)
    # sett inn i db
    cursor = conn.cursor()    
    #('1.0', 'true', '5', 'ARBEIDSLIV', 0)
    cursor.executemany(""" insert IGNORE into emne (versjon, er_hovedtema, id, navn, hovedtema_id) values (%s, %s, %s, %s, %s)""", emne_liste)
    print "%s row inserted" % cursor.rowcount
    conn.commit()

def get_fylker():
    """ get counties from data-stortinget.no """
    url = "http://data.stortinget.no/eksport/fylker"
    r = requests.get(url)  # functions: r.status_code, r.headers['content-type'], r.content
    soup = BeautifulSoup(r.content)
    counties = []
    for co in soup.find_all('fylke'):
        #print co.id.text, co.navn.text
        county = (co.id.text, co.navn.text)
        counties.append(county)
    # sett inn i db
    cursor = conn.cursor()    
    cursor.executemany(""" insert IGNORE into fylker (id, navn) values (%s, %s)""", counties)
    print "%s row inserted" % cursor.rowcount
    conn.commit()

def get_partier(sesjonid):
    url = "http://data.stortinget.no/eksport/partier?sesjonid=%s" % (sesjonid)

def get_alle_partier():
    url = "http://data.stortinget.no/eksport/allepartier"
    r = requests.get(url)  # functions: r.status_code, r.headers['content-type'], r.content
    soup = BeautifulSoup(r.content)
    partier = []
    for par in soup.find_all('parti'):
        partier.append( (par.versjon.text, par.id.text, par.navn.text) )
    cursor = conn.cursor()    
    cursor.executemany(""" insert IGNORE into allepartier (versjon, id, navn) values (%s, %s, %s)""", partier)
    print "%s row inserted (partier)" % cursor.rowcount
    conn.commit()

def get_kommiteer(sesjonid):
    url = "http://data.stortinget.no/eksport/komiteer?sesjonid=%s" % (sesjonid)

def get_alle_komiteer():
    url = "http://data.stortinget.no/eksport/allekomiteer"
    r = requests.get(url)  # functions: r.status_code, r.headers['content-type'], r.content
    soup = BeautifulSoup(r.content)
    komiteer = []
    for kom in soup.find_all('komite'):
        komiteer.append( (kom.versjon.text, kom.id.text, kom.navn.text) )
    cursor = conn.cursor()    
    cursor.executemany(""" insert IGNORE into allekomiteer (versjon, id, navn) values (%s, %s, %s)""", komiteer)
    print "%s row inserted (komiteer)" % cursor.rowcount
    conn.commit()

def get_representanter(stortingsperiodeid):
    url = "http://data.stortinget.no/eksport/representanter?stortingsperiodeid=%s" % (stortingsperiodeid)

def get_dagensrepresentanter():
    """ krever to tabeller: dagensrepresentanter, og folkevalgt_sitter_i_kommite """
    url = "http://data.stortinget.no/eksport/dagensrepresentanter"
    
def get_sporretimesporsmal(sesjonid):
    url = "http://data.stortinget.no/eksport/sporretimesporsmal?sesjonid=%s" % (sesjonid)

def get_interpellasjoner(sesjonid):
    url = "http://data.stortinget.no/eksport/interpellasjoner?sesjonid=%s" % (sesjonid)

def get_skriftligesporsmal(sesjonid):
    url = "http://data.stortinget.no/eksport/skriftligesporsmal?sesjonid=%s" % (sesjonid)

def get_saker(sesjonid):
    """ trenger relasjoner til tre (3) tabeller: 
    - emne (1:n),                                                                           # har tbl : emne
    - komiteer (1:1) (alle eller kun denne sesjonens?, hvor skal det reffes?)               # har tbl : allekomiteer
    - representanter (1:n) (alle, eller kun denne sesjonens?) (denne har jeg ikke)          # har tbl : ???
    """
    url = "http://data.stortinget.no/eksport/saker?sesjonid=%s" % (sesjonid)

def get_voteringer(sakid):
    url = "http://data.stortinget.no/eksport/voteringer?sakid=%s" % (sakid)

def get_voteringsforslag(voteringid):
    url = "http://data.stortinget.no/eksport/voteringsforslag?voteringid=%s" % (voteringid)

def get_voteringsvedtak(voteringid):
    url = "http://data.stortinget.no/eksport/voteringsvedtak?voteringid=%s" % (voteringid)

def get_voteringsresultat(voteringid):
    url = "http://data.stortinget.no/eksport/voteringsresultat?VoteringId=%s" % (voteringid)

def main():
    # get_voteringsresultat('1499')
    # get_voteringsvedtak('1499')
    # get_voteringsforslag('1499')
    # get_voteringer('50135')
    # get_saker('2011-2012')    
    # get_skriftligesporsmal('2011-2012')
    # get_interpellasjoner('2011-2012')
    # get_sporretimesporsmal('2011-2012')
    # get_dagensrepresentanter()
    # get_representanter('2009-2013')
    ##get_alle_komiteer()
    # get_kommiteer('2011-2012')
    ##get_alle_partier()
    # get_partier('2011-2012')
    ##get_fylker()
    ##get_emner()
    ##get_sesjoner()
    ##get_stortingsperioder()
	#pass


if __name__ == '__main__':
	main()

