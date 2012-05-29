#Fra data.stortinget.no til mysql

For å finne ut hva som skjuler seg i stortingets data foretrekker jeg å undersøke dataen med SQL, og dermed trens en måte å få data fra stortinget over i en database. Dette prosjektet har som mål å gjøre just det.

Målet er å skrive funksjoner for alle URler der det kan hentes data. 
Alle funksjonene skal kunne hente ny data hvis der finnes.

Jeg har tenkt at funksjonene skal kunne settes som via crontab slik at ny data kan hentes ved behov.



## databaseskjema
Det ligger nå ved et databaseskjema som kan bruke til å opprette tabeller. Tanken jeg gikk for var å bruke solide primær- og kombinasjonsnøkler slik at INSERT IGNORT statments kan brukes til å sette inn "det som ikke finnes fra før". 


##Avhengigheter til andre python bibliotek
Jeg har forsøkt å gjøre dette så enkelt som mulig for meg, det betyr å bruke andre bibliotek der jeg har funnet det nyttig.

* import [requests](http://kennethreitz.com/requests-python-http-module.html)
* from bs4 import [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) 
* import xml.etree.cElementTree as [et](http://lxml.de/) eller var det http://effbot.org/zone/celementtree.htm ?
* import [MySQLdb](http://mysql-python.sourceforge.net/)


-E

### jeg leker med markdown..

> sitat
> mer sitat

*eple
*pære
*banan

1. krabbe
2. gå
3. løpe



###Kode:
    print "Hei verden"


