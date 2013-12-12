#!/usr/bin/env python

################################################
#	Program prolazi kroz BGP dump, biljezi pojavljivanje parova
#	AS-prefiks, odnosno koliko se puta pojedini AS nalazi u PATHU za pojedini prefiks.
#	
#	Prikazuje se ispis AS-ova, gdje se za pojedini AS ispisuju
#	svi prefiksi koji su imali ili imaju taj AS u svom PATH-u.
#	Takodjer se ispisuje broj takvih parova.
#
#	Broja AS-ova>>> 		  Ukupan broj AS-ova u ovom BGP dumpu
#	Broj parova prefiks-AS>>> 	  Ukupan broj svih parova prefiks-AS
#	Ukupan broj objava prefiks-AS>>>  Ukupan broj svih objava svih parova
#
#	Prosjek prefiksa po AS-u>>>        	Omjer parova prefiks-AS i broja AS-ova
#	Prosjek objava prefiksa po AS-u>>> 	Omjer svih objava parova i broja AS-ova
#	Prosjek objava i parova pref-AS>>>	Omjer svih objava parova i broja parova prefiks-AS
#
#	[ [AS1, [p11, p12,..., p1n]	
#	  [AS2, [p21, p22,..., p2n]	
#         ...
#         [ASm, [pm1, pm2,..., pmn]  ]
#
################################################

from pybgpdump import BGPDump
import socket
import struct
import sys
import time
import os.path

as_prefix=[]			#lista parova AS-prefiks s brojem objava parova
povuceni_pref=[]
as_withdrawn=[]
pojavljivanje_ASa=0
pojavljivanje_prefiksa=0
povucen_prefiks=0

pomocni=1

lista_prefiksa=[]		#pomocne liste
zapis_zaAS=[]

broj_ASova=0			#razni brojaci
broj_prefiksa=0


dircur = os.getcwd()

if (len(sys.argv)>=2):
	d=BGPDump((dircur+ "/dumpovi/" +sys.argv[1]))
else:
	d=BGPDump((dircur + '/dumpovi/proba'))

f = open(dircur + '/ispisi/AS_prefiks_withdrawn', 'w')

for mrth,bgph,bgpm in d:

	if bgpm.data.announced:
		for el in bgpm.data.attributes:			#od svih atributa u pojedinom updateu
			if el.type==2:				# type=2 znaci da je atribut AS path
				for seg in el.data.segments:
       					for AS in seg.path:
	
						if pomocni==1:
							print "."
							pomocni=2
						elif pomocni==2:
							print ".."
							pomocni=3
						elif pomocni==3:
							print "..."
							pomocni=4
						elif pomocni==4:
							print "...."
							pomocni=1
		
						pojavljivanje_ASa=0
						for ases in as_prefix:	#gledamo da li vec postoji zapis za ovaj AS	
							if ((ases[0]) == (AS)):
								pojavljivanje_ASa=1
								break
												
						if pojavljivanje_ASa==1:
							
							for zapis in as_prefix:		#trazimo zapis za ovaj AS
								if (zapis[0]==AS):
									for ek in bgpm.data.announced:
										temp = socket.inet_ntoa(ek.prefix)+"/"+str(ek.len)
										if ((zapis[1]).count(temp))==0:
											zapis[1].append(temp)
									break
								

						if pojavljivanje_ASa==0:
							lista_prefiksa=[]
							lista_prefiksa.append(AS)
							lista_prefiksa.append([])	
							for ek in bgpm.data.announced:	#popunimo listu za novi AS
								temp = socket.inet_ntoa(ek.prefix)+"/"+str(ek.len)
								lista_prefiksa[1].append(temp)
							as_prefix.append(lista_prefiksa)
							


	elif bgpm.data.withdrawn:
							
		for zapis in as_prefix:
			as_temp=zapis[0]		
			for ek in bgpm.data.withdrawn:
				
				povucen_prefiks=0
				temp = socket.inet_ntoa(ek.prefix)+"/"+str(ek.len)
				if ((zapis[1]).count(temp))!=0:		#nema zapisa za taj pref.
					
					if (len(zapis[1])==1):
						as_prefix.remove(zapis)
						povucen_prefiks=1
						break
					
					else:
						(zapis[1]).remove(temp)
						povucen_prefiks=1
				
				if povucen_prefiks==1:

					#spremi povucen prefiks u listu
					pojavljivanje_ASa=0
					for pov in povuceni_pref:
						if ((pov[0]) == as_temp):
							pojavljivanje_ASa=1
							break
					
					if pojavljivanje_ASa==1:
						if ((pov[1]).count(temp))==0:
							(pov[1]).append(temp)
							broj_prefiksa=broj_prefiksa+1
					
					else:
						povuceni_pref.append([as_temp,[temp]])
						broj_ASova=broj_ASova+1
						broj_prefiksa=broj_prefiksa+1
						
						
									

for AS in povuceni_pref:

	print "\n"
	print " ---------------------------- "
	print "\n  AS\n"

	print "  " + str(AS[0])
	print "\n"

	for pr in AS[1]:
		
		print "          \t " + str(pr)


print "\n\n"

print " Broj AS-ova>>>                \t " + str(broj_ASova)
print " Broj povucenih prefiksa>>>    \t " + str(broj_prefiksa)

print "\n\n"

f.close()
