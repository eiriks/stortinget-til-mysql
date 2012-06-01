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


# søk etter medier i spørsmål 
søk er case-insensitift (ingen bokstavkjenslevarlei)

* aftenposten 		291
* " vg "				127		(søket innehold mellomrom før og etter VG)
* Verdens gang		30
* Vårt land			60 		(her er det selvsagt noen feil)
* Dagbladet			128
* nrk					342		(rimelig å anta at det også er de del spørsmål om finansiering/drift osv av nrk)
    * brennpunkt			11
* Bergens tidene		1
* nationen			63
* se og hør			1
* agderposten			16
* TV2					96
    * dokument 2			2		(en av disse omhandler ikke TV2 på noen måte)
* TV3					2
* kapital				203		(innlysende mye som ikke er T. Hegnars her)
* tv-norge			2		(og er om, ikke fra tv-norge)
* stavanger aftenblad	63
* adresseavisa		4
* drammens tidene		2
* nettavisen			11
* klassekampen		31
* Altaposten			4
* Arendals Tidende	1
* Bergensavisen		7
* Østlendingen		18
* Østlandets Blad		4
* Varden				9
* Tønsbergs Blad		2

Hvis jeg summerer disse 28 søkene (≈1530, som er urimelig uten å sjekke for feil og i hvilken grad de er overlappende) og deler på antall spørsmål i basen (ca30k) får vi 0.05*100≈5%.
** Altså (veldig røfflig) at 5% av spørsmålene som leveres inneholder en referanse til medier **. 
Det er 

1. metodiske slappt arbeid
2. helt sikkert feil (men hvem vet hvor feil det er?)

men er det for lite? Eller mye?
Kan det hende at kun 5% av spørsmålene er fra ting som mediene graver fram?


#####Flere søkeord
* avisen			243		
* fjernsyn		46
* " TV "			36
* " TV-"			62
* radio			163		(er er det mye som ikke omhandler nyhetsmedier)

som også er ganske lite..


## jeg leker med markdown..

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


