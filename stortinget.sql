# denne er autogrnerert fra sequelPro - et glimrende gratis GUI til mySQL
# -Eirik
# ************************************************************
# Sequel Pro SQL dump
# Version 3408
#
# http://www.sequelpro.com/
# http://code.google.com/p/sequel-pro/
#
# Host: localhost (MySQL 5.5.9)
# Database: stortinget
# Generation Time: 2012-05-22 17:24:14 +0200
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Dump of table allekomiteer
# ------------------------------------------------------------

CREATE TABLE `allekomiteer` (
  `id` varchar(50) NOT NULL DEFAULT '',
  `versjon` varchar(50) DEFAULT NULL,
  `navn` varchar(200) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table allepartier
# ------------------------------------------------------------

CREATE TABLE `allepartier` (
  `id` varchar(10) NOT NULL DEFAULT '',
  `versjon` varchar(50) DEFAULT NULL,
  `navn` varchar(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table emne
# ------------------------------------------------------------

CREATE TABLE `emne` (
  `id` int(5) unsigned NOT NULL,
  `navn` varchar(100) NOT NULL DEFAULT '',
  `er_hovedtema` varchar(50) DEFAULT NULL,
  `versjon` varchar(10) DEFAULT NULL,
  `hovedtema_id` int(5) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='hovedtema_id er 0 hvis temaet er et hovedtema, det er ID''n til hovedtemaet hvis temaet er et undertema.';



# Dump of table fylker
# ------------------------------------------------------------

CREATE TABLE `fylker` (
  `id` varchar(2) NOT NULL DEFAULT '',
  `navn` varchar(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table kommiteer_per_sesjon
# ------------------------------------------------------------

CREATE TABLE `kommiteer_per_sesjon` (
  `sesjonid` varchar(11) NOT NULL DEFAULT '',
  `versjon` varchar(20) DEFAULT NULL,
  `komiteid` varchar(50) NOT NULL DEFAULT '',
  `komitenavn` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`sesjonid`,`komiteid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='her er det en kombinasjonsnøkkel (sesjonid og komiteid) for å sikre at insert ignore fungerer som det skal.';



# Dump of table partier_per_sesjon
# ------------------------------------------------------------

CREATE TABLE `partier_per_sesjon` (
  `versjon` varchar(20) DEFAULT NULL,
  `partiid` varchar(10) NOT NULL DEFAULT '',
  `partinavn` varchar(100) DEFAULT '',
  `sesjonid` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`sesjonid`,`partiid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='her er det den kombinasjonsnøkkel (sesjonid + partiid) som sikrer at "insert IGNORE" fungere som det skal.';



# Dump of table representanter
# ------------------------------------------------------------

CREATE TABLE `representanter` (
  `id` varchar(11) NOT NULL DEFAULT '',
  `stortingsperiodeid` varchar(50) NOT NULL DEFAULT '',
  `versjon` varchar(50) DEFAULT NULL,
  `doedsdato` datetime DEFAULT NULL,
  `etternavn` varchar(50) DEFAULT NULL,
  `foedselsdato` datetime DEFAULT NULL,
  `fornavn` varchar(50) DEFAULT NULL,
  `kjoenn` varchar(6) DEFAULT NULL,
  `fylke_id` varchar(2) NOT NULL DEFAULT '',
  `parti_id` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table sak_emne
# ------------------------------------------------------------

CREATE TABLE `sak_emne` (
  `saksid` int(11) NOT NULL DEFAULT '0',
  `emneid` int(5) NOT NULL DEFAULT '0',
  PRIMARY KEY (`saksid`,`emneid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='burde jeg har hatt sesjon her også? hvis saksid er unik bør det være unødvendig';



# Dump of table sak_saksordfoerer
# ------------------------------------------------------------

CREATE TABLE `sak_saksordfoerer` (
  `saksid` int(11) NOT NULL DEFAULT '0',
  `saksordfoerer` varchar(11) NOT NULL DEFAULT '',
  PRIMARY KEY (`saksid`,`saksordfoerer`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table sak_votering
# ------------------------------------------------------------

CREATE TABLE `sak_votering` (
  `sak_id` int(11) NOT NULL DEFAULT '0',
  `versjon` varchar(50) DEFAULT NULL,
  `alternativ_votering_id` int(11) DEFAULT NULL,
  `antall_for` int(11) DEFAULT NULL,
  `antall_ikke_tilstede` int(11) DEFAULT NULL,
  `antall_mot` int(11) DEFAULT NULL,
  `behandlingsrekkefoelge` int(5) DEFAULT NULL,
  `dagsorden_sak_nummer` int(5) DEFAULT NULL,
  `fri_votering` varchar(100) DEFAULT NULL,
  `kommentar` varchar(256) DEFAULT NULL COMMENT 'brukes denne?',
  `mote_kart_nummer` int(11) DEFAULT NULL,
  `personlig_votering` varchar(100) DEFAULT NULL,
  `presidentid` varchar(11) DEFAULT NULL,
  `vedtatt` varchar(20) DEFAULT NULL,
  `votering_id` int(11) NOT NULL DEFAULT '0',
  `votering_metode` varchar(100) DEFAULT NULL,
  `votering_resultat_type` varchar(100) DEFAULT NULL,
  `votering_resultat_type_tekst` varchar(100) DEFAULT NULL,
  `votering_tema` varchar(200) DEFAULT NULL,
  `votering_tid` datetime DEFAULT NULL,
  PRIMARY KEY (`sak_id`,`votering_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table saker
# ------------------------------------------------------------

CREATE TABLE `saker` (
  `id` int(11) unsigned NOT NULL,
  `versjon` varchar(50) DEFAULT NULL,
  `behandlet_sesjon_id` varchar(50) DEFAULT NULL,
  `dokumentgruppe` varchar(100) DEFAULT NULL,
  `henvisning` varchar(200) DEFAULT NULL,
  `innstilling_id` int(11) DEFAULT NULL COMMENT 'hva er dette, egentlig?',
  `komiteid` varchar(50) DEFAULT NULL,
  `komitenavn` varchar(200) DEFAULT NULL,
  `korttittel` varchar(256) DEFAULT NULL,
  `sak_fremmet_id` int(11) DEFAULT NULL COMMENT 'hva er dette, egentlig?',
  `sist_oppdatert_dato` datetime DEFAULT NULL,
  `status` varchar(200) DEFAULT NULL,
  `tittel` text,
  `type` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table sesjoner
# ------------------------------------------------------------

CREATE TABLE `sesjoner` (
  `id` varchar(50) NOT NULL DEFAULT '',
  `versjon` varchar(50) DEFAULT NULL,
  `fra` datetime NOT NULL,
  `til` datetime NOT NULL,
  `er_innevaerende` int(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='er_innevaerende er 1 hvis dette er inneværrende sesjon';



# Dump of table sporsmal
# ------------------------------------------------------------

CREATE TABLE `sporsmal` (
  `id` int(11) unsigned NOT NULL,
  `sesjonid` varchar(50) DEFAULT NULL,
  `versjon` varchar(20) DEFAULT NULL,
  `besvart_av` varchar(11) DEFAULT NULL,
  `besvart_av_minister_id` varchar(11) DEFAULT NULL,
  `besvart_av_minister_tittel` varchar(200) DEFAULT NULL,
  `besvart_dato` datetime DEFAULT NULL,
  `pa_vegne_av` varchar(100) DEFAULT NULL COMMENT 'brukes?',
  `besvart_pa_vegne_av_minister_id` varchar(11) DEFAULT NULL,
  `besvart_pa_vegne_av_minister_tittel` varchar(200) DEFAULT NULL,
  `datert_dato` datetime DEFAULT NULL,
  `flyttet_til` varchar(100) DEFAULT NULL,
  `fremsatt_av_annen` varchar(11) DEFAULT NULL,
  `rette_vedkommende` varchar(11) DEFAULT NULL,
  `rette_vedkommende_minister_id` varchar(11) DEFAULT NULL,
  `rette_vedkommende_minister_tittel` varchar(200) DEFAULT NULL,
  `sendt_dato` datetime DEFAULT NULL,
  `sporsmal_fra` varchar(11) DEFAULT NULL COMMENT 'så lenge det er 1:1 mot representanter',
  `sporsmal_nummer` int(10) DEFAULT NULL,
  `sporsmal_til` varchar(11) DEFAULT NULL COMMENT 'så lenge det er 1:1 mot representanter',
  `sporsmal_til_minister_id` varchar(11) DEFAULT NULL,
  `sporsmal_til_minister_tittel` varchar(200) DEFAULT NULL,
  `status` varchar(200) DEFAULT NULL,
  `tittel` text,
  `type` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='type angir om det er 1) skriftlig_sporsmal, 2) interpellasjon eller 3) spørretimespørsmål som er en av: sporretime_sporsmal, muntlig_sporsmal eller ved noen tilfeller: ikke_spesifisert';



# Dump of table sporsmal_emne
# ------------------------------------------------------------

CREATE TABLE `sporsmal_emne` (
  `sporsmalid` int(11) NOT NULL DEFAULT '0',
  `emneid` int(5) NOT NULL DEFAULT '0',
  PRIMARY KEY (`sporsmalid`,`emneid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table stortingsperioder
# ------------------------------------------------------------

CREATE TABLE `stortingsperioder` (
  `id` varchar(50) NOT NULL DEFAULT '',
  `versjon` varchar(50) DEFAULT NULL,
  `fra` datetime NOT NULL,
  `til` datetime NOT NULL,
  `er_innevaerende` int(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table voteringsforslag
# ------------------------------------------------------------

CREATE TABLE `voteringsforslag` (
  `voteringid` int(11) NOT NULL DEFAULT '0',
  `forslag_id` int(11) NOT NULL DEFAULT '0',
  `versjon` varchar(10) DEFAULT NULL,
  `forslag_betegnelse` varchar(150) DEFAULT NULL,
  `forslag_betegnelse_kort` varchar(100) DEFAULT NULL,
  `forslag_levert_av_representant` varchar(200) DEFAULT NULL,
  `forslag_paa_vegne_av_tekst` varchar(100) DEFAULT NULL,
  `forslag_sorteringsnummer` int(11) DEFAULT NULL,
  `forslag_tekst` mediumtext COMMENT 'TEXT ble for kort?',
  `forslag_type` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`voteringid`,`forslag_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table voteringsresultat
# ------------------------------------------------------------

CREATE TABLE `voteringsresultat` (
  `voteringid` int(11) NOT NULL DEFAULT '0',
  `representant_id` varchar(11) NOT NULL DEFAULT '',
  `versjon` varchar(50) DEFAULT NULL,
  `fast_vara_for` varchar(11) DEFAULT NULL,
  `vara_for` varchar(11) DEFAULT NULL,
  `votering` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`voteringid`,`representant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table voteringsvedtak
# ------------------------------------------------------------

CREATE TABLE `voteringsvedtak` (
  `voteringid` int(11) NOT NULL DEFAULT '0',
  `versjon` varchar(50) DEFAULT NULL,
  `vedtak_kode` varchar(100) DEFAULT NULL,
  `vedtak_kommentar` varchar(256) DEFAULT '',
  `vedtak_nummer` int(11) NOT NULL DEFAULT '0',
  `vedtak_referanse` varchar(200) DEFAULT NULL,
  `vedtak_tekst` text,
  PRIMARY KEY (`voteringid`,`vedtak_nummer`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;




/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
