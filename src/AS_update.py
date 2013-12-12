#!/usr/bin/env python

################################################
#	Program prolazi kroz BGP dump, biljezi pojavljivanje pojedinih AS-ova,
#	te broji koliko puta se pojavio pojedini AS kroz sve Update poruke.
#	Pritom nije bitno koliko se prefiksa objavila s putem kroz pojedini AS,
#	vec je bitno samo u koliko se Update-a pojavio pojedini AS
#	
#	Broja AS-ova>>> 	  Ukupan broj AS-ova u ovom BGP dumpu.
#	Broj pojavljivanja>>> 	  Broj Update poruka u kojima se pojavljuje pojedini AS
#	Pojavljivanja po AS-u>>>  Omjer prethodne dvije vrijednosti
#
################################################

from pybgpdump import BGPDump
import socket
import struct
import sys
import time
import os.path

as_prefix=[]		#lista parova AS-prefiks
pojavljivanje=0
ukupno_pojavljivanja=0
broj_ASova=0

dircur = os.getcwd()

if (len(sys.argv)>=2):
	d=BGPDump((dircur+ "/dumpovi/" +sys.argv[1]))
else:
	d=BGPDump((dircur + '/dumpovi/proba'))
	#d=BGPDump((dircur + "/dumps/updates.20110201.0000.bz2"))
	

f = open(dircur + '/ispisi/AS_update_ispis', 'w')

for mrth,bgph,bgpm in d:

	for el in bgpm.data.attributes:			#od svih atributa u pojedinom updateu
		if el.type==2:				# type=2 znaci da je atribut AS path
			for seg in el.data.segments:
       				for AS in seg.path:
					pojavljivanje=0
					for ases in as_prefix:			#gledamo da li vec postoji zapis za ovaj AS
						if ((ases[0]) == (AS)):
							ases[1] = ases[1]+1
							pojavljivanje=1
							ukupno_pojavljivanja=ukupno_pojavljivanja+1
							break
					if pojavljivanje==0:			#ako ne postoji zapis za ovaj AS
						as_prefix.append([AS,1])	#dodamo ovaj AS u listu
						ukupno_pojavljivanja=ukupno_pojavljivanja+1
						broj_ASova=broj_ASova+1

print "\n"
f.write("\n\n")
print "  AS    \t broj pojavljivanja"
f.write("\n  AS    \t broj pojavljivanja")
print " ------------------------------- "
f.write("\n ------------------------------- ")


for AS in as_prefix:
	
	print "  " + str(AS[0]) + "   \t " + str(AS[1])
	f.write("\n  " + str(AS[0]) + "   \t " + str(AS[1]))

print "\n"
f.write("\n\n")
print "  AS    \t broj pojavljivanja"
f.write("\n  AS    \t broj pojavljivanja")
print " ------------------------------------------ "
f.write("\n ------------------------------------------ ")

print "\n"
f.write("\n\n")
print "Broja AS-ova>>>          \t " + str(broj_ASova)	
f.write("\nBroja AS-ova>>>          \t " + str(broj_ASova))
print "Broj pojavljivanja>>>    \t " + str(ukupno_pojavljivanja)
f.write("\nBroj pojavljivanja>>>    \t " + str(ukupno_pojavljivanja))
print "Pojavljivanja po AS-u>>> \t " + str(float(ukupno_pojavljivanja)/broj_ASova)
f.write("\nPojavljivanja po AS-u>>> \t " + str(float(ukupno_pojavljivanja)/broj_ASova))
print "\n"
f.write("\n\n\n")

f.close()

print "\n  Podaci su zapisani u datoteku " + dircur + '/ispisi/AS_update_ispis'


