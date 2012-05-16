#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by Eirik Stavelin on 2012-05-09.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.

Denne koden er å ansees som public domain ala MIT-lisensen eller "gjør-hva-du-vil,-men-ikke-klag-til-meg" lisensen.


"""

import sys
import os
import requests         # http://kennethreitz.com/requests-python-http-module.html
#import json
import time
from bs4 import BeautifulSoup
import xml.etree.cElementTree as et
import MySQLdb
conn = MySQLdb.connect(host = "localhost", user = "root", passwd = "root", db = "stortinget", charset='utf8') # dette må du naturlig nok tilpasse din egen maskin..


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
    """ dette er de som er inne (aka over sperregrensen) per stortingsvalg. (tror jeg)"""
    url = "http://data.stortinget.no/eksport/partier?sesjonid=%s" % (sesjonid)
    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    #print soup
    partier = []
    for parti in soup.find_all('parti'):
        et_parti = (sesjonid, parti.versjon.text, parti.id.text, parti.navn.text)
        partier.append(et_parti)
    #print partier
    cursor = conn.cursor()    
    cursor.executemany(""" insert IGNORE into partier_per_sesjon (sesjonid, versjon, partiid, partinavn) values (%s, %s, %s, %s)""", partier)
    print "%s row(s) inserted (partier) for sesjonen %s" % (cursor.rowcount, sesjonid)
    conn.commit()

def batch_fetch_alle_partier_pr_sessjon():
    """ auxiliary funksjon for å kjøre get_partier for alle sessjoner """
    cursor = conn.cursor() #    1.0 1986-10-01T00:00:00 1986-87 1987-09-30T23:59:59
    cursor.execute("""SELECT id FROM sesjoner""")
    results = cursor.fetchall()
    for result in results:
        get_partier(result[0])
        #sys.exit("det holder med en runde")

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
    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    #print soup
    kommiteer = []
    for kom in soup.find_all('komite'):
        komite = (sesjonid, kom.versjon.text, kom.id.text, kom.navn.text)
        kommiteer.append(komite)
    cursor = conn.cursor()
    
    cursor.executemany(""" insert IGNORE into kommiteer_per_sesjon (sesjonid, versjon, komiteid, komitenavn) values (%s, %s, %s, %s)""", kommiteer)
    print "%s row(s) inserted (komiteer) i sesjon: %s" % (cursor.rowcount, sesjonid)
    conn.commit()

def batch_fetch_alle_kommiteer_pr_sessjon():
    """ auxiliary funksjon for å kjøre get_kommiteer for alle sessjoner """
    cursor = conn.cursor()
    cursor.execute("""SELECT id FROM sesjoner""")
    results = cursor.fetchall()
    for result in results:
        get_kommiteer(result[0])
        #sys.exit("det holder med en runde")


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
    """ """
    url = "http://data.stortinget.no/eksport/representanter?stortingsperiodeid=%s" % (stortingsperiodeid)
    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    representanter = []
    for rep in soup.find_all('representant'):
        # ikke alle representanter har fylke (det er kanskje pussig, men dog.)
        try:
            fylkeid = rep.fylke.id.text
        except:
            fylkeid = ''          # noen bedre måte å indikere at det ikke er noen fylke på (på to bokstaver, eller NULL??)
        representanter.append( (stortingsperiodeid, rep.id.text, rep.versjon.text, rep.doedsdato.text, rep.etternavn.text, rep.foedselsdato.text, rep.fornavn.text, rep.kjoenn.text, fylkeid, rep.parti.id.text) )
    # representanter: stortingsperiodeid, versjon, doedsdato, etternavn, foedselsdato, fornavn, id, kjoenn, fylke_id, parti_id
    cursor = conn.cursor()
    cursor.executemany(""" insert IGNORE into representanter (stortingsperiodeid, id, versjon, doedsdato, etternavn, foedselsdato, fornavn, kjoenn, fylke_id, parti_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", representanter)
    print "%s row(s) inserted (representanter) for perioden %s " % (cursor.rowcount, stortingsperiodeid)
    conn.commit()

def batch_fetch_alle_representanter():
    """ auxiliary funksjon for å kjøre get_representanter for alle stortingsperioder """
    cursor = conn.cursor() #    1.0 1986-10-01T00:00:00 1986-87 1987-09-30T23:59:59
    cursor.execute("""SELECT id FROM stortingsperioder""")
    results = cursor.fetchall()
    for result in results:
        get_representanter(result[0])
    

def get_dagensrepresentanter():
    """ krever to tabeller: dagensrepresentanter, og folkevalgt_sitter_i_kommite """
    # skal jeg bale med lekasjoner til vara-plassene??
    # dette er hovedsaklig redundant data, det eneste som er "nytt" er relaksjon til komiteer og vara-funksjoner....
    url = "http://data.stortinget.no/eksport/dagensrepresentanter"
    
    # skal bli databasetabell
    #dagensrepresentanter: id (erstatter: versjon, doedsdato, etternavn, foedselsdato, fornavn, kjoenn, fylke & parti), fast_vara_for, ref:(1:n) komiteer, vara_for (ukjent, alltid nil=true, sikkert en ref til representantid hvis aktuell? aka varchar(20).)
    # og
    #folkevalgt_sitter_i_kommite: folkvalgtid, komiteid, sesjonid
    
def get_sporretimesporsmal(sesjonid):
    url = "http://data.stortinget.no/eksport/sporretimesporsmal?sesjonid=%s" % (sesjonid)

def get_interpellasjoner(sesjonid):
    url = "http://data.stortinget.no/eksport/interpellasjoner?sesjonid=%s" % (sesjonid)

def get_skriftligesporsmal(sesjonid):
    url = "http://data.stortinget.no/eksport/skriftligesporsmal?sesjonid=%s" % (sesjonid)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "xml")
    #alle_sporsmaal = []
    for spor in soup.find_all('sporsmal'):
        try:
            pa_vegne_av = spor.besvart_pa_vegne_av.id.text
        except:
            pa_vegne_av = ''
        try:
            besvart_pa_vegne_av_minister_id = spor.besvart_pa_vegne_av_minister_id.text
        except:
            besvart_pa_vegne_av_minister_id = ''
        try: 
            besvart_pa_vegne_av_minister_tittel = spor.besvart_pa_vegne_av_minister_tittel.text
        except:
            besvart_pa_vegne_av_minister_tittel = ''
        try:
            rette_vedkommende = spor.rette_vedkommende.id.text
        except:
            rette_vedkommende = '' #False
        try:
            rette_vedkommende_minister_id = spor.rette_vedkommende_minister_id.text
        except:
            rette_vedkommende_minister_id = ''#False
        try:
            rette_vedkommende_minister_tittel = spor.rette_vedkommende_minister_tittel.text
        except:
            rette_vedkommende_minister_tittel = ''#False
        try:
            fremsatt_av_annen = spor.fremsatt_av_annen.id.text
            # her er også andre variabler relavant:
            # versjon, doedsdato, etternavn, foedselsdato, fornavn, id, kjoenn, (+ fylke & parti, som kan være 'nil' her...)
        except:
            fremsatt_av_annen = ''#False
        
        et_sporsmaal = (
                    ##    spor.id.text,                                    #dette er feil se http://stackoverflow.com/questions/10592462/parsing-xml-with-beautifulsoup-multiple-tags-with-same-name-how-to-find-the-r
                    spor.find("id", recursive=False).text,  #alt ok
                    #spor.sesjon_id.text,                   #alt ok - nøkkel mot sesjoner - diplikat av input. jeg bruker innput
                    sesjonid,                              #alt ok
                    spor.versjon.text,                     #alt ok
                    spor.besvart_av.id.text,               #alt ok
                    spor.besvart_av_minister_id.text,      #alt ok
                    spor.besvart_av_minister_tittel.text,  #alt ok
                    spor.besvart_dato.text,                #alt ok
                    pa_vegne_av,                           #alt ok
                    besvart_pa_vegne_av_minister_id,       #alt ok
                    besvart_pa_vegne_av_minister_tittel,   #alt ok
                    spor.datert_dato.text,                 #alt ok
                    #spor.emne_liste,                                
                    # denne brukes ikke i skriftligesporsmal, kan være 1:n på de andre, står det i manualen..
                    spor.flyttet_til.text,                 #alt ok # "ikke spesifisert" er default.. "rette_vedkommende" brukes når ting er flyttet
                    fremsatt_av_annen,                    
                    # dette er en ref til representanter igjen?
                    # nei - dette er folk som IKKE er representanter (aka finnes i representanter-tabellen)
                    # skal jeg lagre dette??
                    rette_vedkommende,                     #alt ok
                    rette_vedkommende_minister_id,         #alt ok
                    rette_vedkommende_minister_tittel,     #alt ok
                    spor.sendt_dato.text,                  #alt ok
                    spor.sporsmal_fra.id.text,             #alt ok - så lenge det er 1:1, nøkkel mot representanter     # kan skriftlige spørsmål bare stilles av folkevalgte??
                    spor.sporsmal_nummer.text,              #alt ok (her er det kompositte nøkler igjen. spørsmålsnummer må være pr år (sesjon, antageligvis))
                    spor.sporsmal_til.id.text,             #alt ok - så lenge det er 1:1, nøkkel mot representanter     # kan skriftlige spørsmål bare stilles til folkevalgte?
                    spor.sporsmal_til_minister_id.text,    #alt ok - nøkkel mot noe?
                    spor.sporsmal_til_minister_tittel.text,#alt ok -fulltekst ministertittel
                    spor.status.text,                       #alt ok
                    spor.tittel.text,                       #alt ok
                    spor.type.text                          #alt ok
                    )
        #print et_sporsmaal
        #alle_sporsmaal.append(et_sporsmaal)
        # reconnect?? fikk stadige "_mysql_exceptions.OperationalError: (2006, 'MySQL server has gone away')"-feil, reconnect ser ut til å funke..
        # når det er veldig mange får jeg en time-out feil. prøver derfor en insert for hvert eneste spørsmål. (størrelsen på den akkumelerte listen blir større en max-verdien min..)
        cursor = conn.cursor()
        cursor.execute(""" insert IGNORE into skriftligesporsmal (id, sesjonid, versjon, besvart_av, besvart_av_minister_id, besvart_av_minister_tittel, besvart_dato, pa_vegne_av, besvart_pa_vegne_av_minister_id, besvart_pa_vegne_av_minister_tittel, datert_dato, flyttet_til, fremsatt_av_annen, rette_vedkommende, rette_vedkommende_minister_id, rette_vedkommende_minister_tittel, sendt_dato, sporsmal_fra, sporsmal_nummer, sporsmal_til, sporsmal_til_minister_id, sporsmal_til_minister_tittel, status, tittel, type) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s)""", et_sporsmaal)
        print "%s row(s) inserted (skriftlige spørsmål) for sesjonen %s, id %s " % (cursor.rowcount, sesjonid.encode('utf8'), spor.find("id", recursive=False).text.encode('utf8'))
        conn.commit()
    # cursor = conn.cursor()
    # cursor.executemany(""" insert IGNORE into skriftligesporsmal (id, sesjonid, versjon, besvart_av, besvart_av_minister_id, besvart_av_minister_tittel, besvart_dato, pa_vegne_av, besvart_pa_vegne_av_minister_id, besvart_pa_vegne_av_minister_tittel, datert_dato, flyttet_til, fremsatt_av_annen, rette_vedkommende, rette_vedkommende_minister_id, rette_vedkommende_minister_tittel, sendt_dato, sporsmal_fra, sporsmal_nummer, sporsmal_til, sporsmal_til_minister_id, sporsmal_til_minister_tittel, status, tittel, type) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s)""", alle_sporsmaal)
    # print "%s row(s) inserted (skriftlige spørsmål) for sesjonen %s " % (cursor.rowcount, sesjonid.encode('utf8'))
    # conn.commit()
    print "Ferdig med sesjon %s" % (sesjonid)

def batch_fetch_alle_skriftligesporsmal():
    """ auxiliary funksjon for å kjøre get_skriftligesporsmal for alle sesjoner """
    cursor = conn.cursor() #    1.0 1986-10-01T00:00:00 1986-87 1987-09-30T23:59:59
    cursor.execute("""SELECT id FROM sesjoner""")
    results = cursor.fetchall()
    for result in results: #[-4:]   [23:]  # finner ikke noe fra før 1996-97 aka results[10:] (finner ikke noe på 11)
        #print result[0]
        get_skriftligesporsmal(result[0])
        #sys.exit("en holder..")
    

def get_saker(sesjonid):
    """ trenger relasjoner til tre (3) tabeller: 
    - emne (1:n),                                                                           # har tbl : emne
    - komiteer (1:1) (alle eller kun denne sesjonens?, hvor skal det reffes?)               # har tbl : allekomiteer
    - representanter (1:n) (alle, eller kun denne sesjonens?)                               # har tbl : representanter
    """
    url = "http://data.stortinget.no/eksport/saker?sesjonid=%s" % (sesjonid)
    #print url
    # http://data.stortinget.no/eksport/saker?sesjonid=2009-2010
    # http://data.stortinget.no/eksport/saker?sesjonid=2009-2010
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "xml")
    #alle_sporsmaal = []
    for sak in soup.find_all('sak'):
        try:
            komiteid = sak.komite.id.text
        except:
            komiteid = ''
        try:
            komitenavn = sak.komite.navn.text
        except:
            komitenavn = ''
        
        sak_emne = []
        if(len(sak.find_all('emne'))>0):             #alle ha emne, bare noen har ref (<emne/> kan være en tom tagg)
            for ref in sak.find_all('emne'):
                sak_emne.append(ref.id.text)
        #print sak_emne
        
        # if (len(ref_til_emne) >10):                                                   # enn så sprøtt et ser ut, så stemmer det at noen omhandler bråtevis med emner..
        #     print sak.behandlet_sesjon_id.text, sak.find("id", recursive=False).text
        
        sak_saksordfoerer = []
        if(len(sak.find_all('representant'))>0):                                        # NB: det går hvist an at det ikke er noen saksordfører også...
            for ref in sak.find_all('representant'):
                sak_saksordfoerer.append(ref.id.text)
            #print len(sak.find_all('representant')), sak.find("id", recursive=False).text
        #print sak_saksordfoerer
        
        en_sak = (
        #sak.id.text,                       #alt ok - ser riktig ut. nei
        sak.find("id", recursive=False).text,
        sak.versjon.text,                  #alt ok
        sak.behandlet_sesjon_id.text,      #alt ok 
        sak.dokumentgruppe.text,           #alt ok
#        #sak.emne_liste,                    #           liste med ider til emner
        sak.henvisning.text,               #alt ok
        sak.innstilling_id.text,           #alt ok - ser rett ut - hva er dette egentlig? ref til hva?          blir ofte "-1" hva er det?
        komiteid,                          #alt ok
        komitenavn,                        #alt ok - ref til allekomiteer eller komite_per_sesjon 
        sak.korttittel.text,               #alt ok
        sak.sak_fremmet_id.text,           #alt ok
#        sak.saksordfoerer_liste,           #           liste med ider til representant(er) 
        sak.sist_oppdatert_dato.text,      #alt ok
        sak.status.text,                   #alt ok
        sak.tittel.text,                   #alt ok
        sak.type.text                      #alt ok
        )
        #print en_sak
        
        # forsøker en-og-en igjen, antar at det kan bli store datamengder her også...
        #først relasjonene:
        cursor = conn.cursor()
        for relasjon in sak_emne:
            cursor.execute(""" insert IGNORE into sak_emne (saksid, emneid) values (%s, %s)""", (sak.find("id", recursive=False).text, relasjon))
            print "%s row(s) inserted (relasjon: sak-emne) saksid-emneid %s-%s " % (cursor.rowcount, sak.find("id", recursive=False).text.encode('utf8'), relasjon.encode('utf8'))
            conn.commit()
        for relasjon in sak_saksordfoerer:            
            cursor.execute(""" insert IGNORE into sak_saksordfoerer (saksid, saksordfoerer) values (%s, %s)""", (sak.find("id", recursive=False).text, relasjon))
            print "%s row(s) inserted (relasjon: sak_saksordfoerer) saksid-representantid %s-%s " % (cursor.rowcount, sak.find("id", recursive=False).text.encode('utf8'),relasjon.encode('utf8'))
            conn.commit()
        # så selve saken:
        cursor.execute(""" insert IGNORE into saker (id, versjon, behandlet_sesjon_id, dokumentgruppe, henvisning, innstilling_id, komiteid, komitenavn, korttittel, sak_fremmet_id, sist_oppdatert_dato, status, tittel, type) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", en_sak)
        print "%s row(s) inserted (saker) for sesjonen %s, id %s " % (cursor.rowcount, sesjonid.encode('utf8'), sak.find("id", recursive=False).text.encode('utf8'))
        conn.commit()
        #print en_sak
        #sys.exit("dø")
    print "ferdig med å sette inn saker for sesjonen %s" % (sesjonid.encode('utf8'))
                
def batch_fetch_alle_saker():
    """ auxiliary funksjon for å kjøre get_saker for alle sesjoner """
    cursor = conn.cursor()
    cursor.execute("""SELECT id FROM sesjoner""")
    results = cursor.fetchall()
    for result in results: #[-4:]   [23:]  # finner ikke noe fra før 1996-97 aka results[10:] (finner ikke noe på 11)
        #print result[0]
        get_saker(result[0])


def get_voteringer(sakid):
    # antar saker har voteringsid, som er det jeg trenger til de siste funksjonene (som virker rimelig)
    url = "http://data.stortinget.no/eksport/voteringer?sakid=%s" % (sakid)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "xml")
    
    voteringer = []
    for vot in soup.find_all('sak_votering'):
        votering = (
        vot.sak_id.text,
        vot.versjon.text,
        vot.alternativ_votering_id.text,
        vot.antall_for.text,
        vot.antall_ikke_tilstede.text,
        vot.antall_mot.text,
        vot.behandlingsrekkefoelge.text,
        vot.dagsorden_sak_nummer.text,
        vot.fri_votering.text,
        vot.kommentar.text,
        vot.mote_kart_nummer.text,
        vot.personlig_votering.text,
        vot.president.id.text,
        vot.vedtatt.text,
        vot.votering_id.text,
        vot.votering_metode.text,
        vot.votering_resultat_type.text,
        vot.votering_resultat_type_tekst.text,
        vot.votering_tema.text,
        vot.votering_tid.text
        )
        #print votering
        
        # dette er en sjekk som feiler hvis det mangler data i xml'n
        #print sakid,vot.sak_id.text
        if int(sakid) == int(vot.sak_id.text):
            # add voteringen til listen over voteringer for denne saken (samme sakid, i alle fall)
            #print votering
            voteringer.append(votering)
    cursor = conn.cursor()
    cursor.executemany(""" insert IGNORE into sak_votering (sak_id, versjon, alternativ_votering_id, antall_for, antall_ikke_tilstede, antall_mot, behandlingsrekkefoelge, dagsorden_sak_nummer, fri_votering, kommentar,mote_kart_nummer, personlig_votering, presidentid, vedtatt, votering_id, votering_metode, votering_resultat_type, votering_resultat_type_tekst, votering_tema, votering_tid) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", voteringer)
    print "%s row(s) inserted - votering for saksid %s " % (cursor.rowcount, sakid)
    conn.commit()
    #sys.exit("stop")

def batch_fetch_alle_voteringer():
    """ auxiliary funksjon for å kjøre get_saker for alle sesjoner """
    cursor = conn.cursor()
    cursor.execute("""SELECT id FROM saker WHERE status = 'behandlet' ORDER BY id DESC""")
    results = cursor.fetchall()
    for result in results: #[-4:]   [23:]  # finner ikke noe fra før 1996-97 aka results[10:] (finner ikke noe på 11)
        #print result[0]
        time.sleep(1.5)     #ikke stresse it@stortinget ?
        get_voteringer(result[0])



def get_voteringsforslag(voteringid):
    """ dette er forslagene som kanskje ledet til en votering?  """
    url = "http://data.stortinget.no/eksport/voteringsforslag?voteringid=%s" % (voteringid)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "xml")
    voteringid_fra_xml = soup.votering_id.text
    vuredringsforslags_liste = []
    for votf in soup.find_all('voteringsforslag'):
        voteringsforslag = (
        voteringid_fra_xml,                         # dette er det samme som input - aka voteringid
        votf.forslag_id.text,
        votf.versjon.text,
        votf.forslag_betegnelse.text,
        votf.forslag_betegnelse_kort.text,
        votf.forslag_levert_av_representant.text,
        votf.forslag_paa_vegne_av_tekst.text,
        votf.forslag_sorteringsnummer.text,
        votf.forslag_tekst.text,
        votf.forslag_type.text
        )
        vuredringsforslags_liste.append(voteringsforslag)
        
    #print voteringid, voteringid_fra_xml
    #print "\n"
    #print len(vuredringsforslags_liste)
    
    cursor = conn.cursor()
    cursor.executemany(""" insert IGNORE into voteringsforslag (voteringid, forslag_id, versjon, forslag_betegnelse, forslag_betegnelse_kort, forslag_levert_av_representant, forslag_paa_vegne_av_tekst, forslag_sorteringsnummer, forslag_tekst, forslag_type) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", vuredringsforslags_liste)
    print "%s row(s) inserted - voteringsforslag for votering %s " % (cursor.rowcount, voteringid)
    conn.commit()
    
    
    
def batch_fetch_alle_voteringsforslag():
    """ auxiliary funksjon for å kjøre get_saker for alle sesjoner """
    cursor = conn.cursor()
    cursor.execute("""SELECT DISTINCT votering_id FROM sak_votering""")     #hvorfor må denne være distinkt? kan flere saker ha samme votering_id? eller er det redundans i sak_votering-tabellen?
    results = cursor.fetchall()
    for result in results:
        time.sleep(1.5)     #ikke stresse it@stortinget ?
        get_voteringsforslag(result[0])

def get_voteringsvedtak(voteringid):
    url = "http://data.stortinget.no/eksport/voteringsvedtak?voteringid=%s" % (voteringid)

def get_voteringsresultat(voteringid):
    url = "http://data.stortinget.no/eksport/voteringsresultat?VoteringId=%s" % (voteringid)

def main():
    # get_voteringsresultat('1499')
    # get_voteringsvedtak('1499')
    batch_fetch_alle_voteringsforslag() # get_voteringsforslag('1499')
    ##batch_fetch_alle_voteringer() # get_voteringer('50135')
    ##batch_fetch_alle_saker() # get_saker('2011-2012')    
    ## batch_fetch_alle_skriftligesporsmal() # get_skriftligesporsmal('2011-2012')
    # get_interpellasjoner('2011-2012')
    # get_sporretimesporsmal('2011-2012')
    # get_dagensrepresentanter()
    ## batch_fetch_alle_representanter() # kjører denne i batch (for each stortingsperiode):     ## get_representanter('2009-2013')
    ##get_alle_komiteer()
    ##batch_fetch_alle_kommiteer_pr_sessjon() # get_kommiteer('2011-2012')
    ##get_alle_partier()
    ##batch_fetch_alle_partier_pr_sessjon() # get_partier('2011-2012')
    ##get_fylker()
    ##get_emner()
    ##get_sesjoner()
    ##get_stortingsperioder()
    pass



if __name__ == '__main__':
	main()

