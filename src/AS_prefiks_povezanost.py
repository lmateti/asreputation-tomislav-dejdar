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
################################################

from pybgpdump import BGPDump
import socket
import struct
import sys
import time
import os.path
import os
import glob

as_prefix=[]			#lista parova AS-prefiks s brojem objava parova
pojavljivanje_ASa=0
pojavljivanje_prefiksa=0

pomocni=1

lista_prefiksa=[]		#pomocne liste
zapis_zaAS=[]

broj_ASova=0			#razni brojaci
broj_parova_prefiks_AS=0
broj_prefiksa_AS=0
broj_pojavljivanja_pref=0
broj_objava_pref_AS=0

dircur = os.getcwd()
os.chdir(dircur + "/dumps")
file_list = glob.glob("*.*")
print file_list
file_list.sort()
print file_list

dump_list=[]
for file_name in file_list:
	dump_list.append(BGPDump(file_name))

f = open(dircur + '/ispisi/AS_prefiks_povezanost_ispis', 'w')

#d=dump_list[0]

for d in dump_list:

	for mrth,bgph,bgpm in d:

		for el in bgpm.data.attributes:			#od svih atributa u pojedinom updateu
			if el.type==2:				# type=2 znaci da je atribut AS path
				as_double=0
				for seg in el.data.segments:
	       				for AS in seg.path:
						if (as_double!=AS):
							as_double=AS

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
							for ases in as_prefix:			#gledamo da li vec postoji zapis za ovaj AS
								if ((ases[0]) == (AS)):
									pojavljivanje_ASa=1
									break

							if bgpm.data.announced:		#prolazimo kroz sve prefikse u objavljenim pref.
								lista_prefiksa=[]

								if pojavljivanje_ASa==0:

									lista_prefiksa.append(AS)	
									for ek in bgpm.data.announced:		#popunimo listu za novi AS
										temp = socket.inet_ntoa(ek.prefix)+"/"+str(ek.len)
										lista_prefiksa.append([temp,1])
									as_prefix.append(lista_prefiksa)
									pojavljivanje_ASa=1

								else:
									for zapis in as_prefix:		#trazimo zapis za ovaj AS
										if (zapis[0]==AS):
											zapis_zaAS=zapis
											as_prefix.remove(zapis)
											break

									zapis.remove(AS)

									for ek in bgpm.data.announced:	
										pojavljivanje_prefiksa=0
										temp = socket.inet_ntoa(ek.prefix)+"/"+str(ek.len)

										for em in zapis:	#azuriramo broj pojavljivanja
											if (em[0]==temp):
												em[1]=em[1]+1
												pojavljivanje_prefiksa=1
												break
										if (pojavljivanje_prefiksa==0):
											zapis.append([temp,1])
							
									zapis.insert(0, AS)
									as_prefix.append(zapis)
						

print "\n"
f.write("\n\n")
print "\n ----------------------------------- "
f.write("\n ----------------------------------- ")
print "\n"
f.write("\n\n")

for AS in as_prefix:

	print "  AS  "
	f.write("\n  AS  ")
	print ""
	f.write("\n")
	print "  " + str(AS[0]) + "  "
	f.write("\n  " + str(AS[0]) + "  ")
	print ""
	f.write("\n")
	print "          \t " + "prefiks        " + "    \t " + "broj objava prefiksa "
	f.write("\n          \t " + "prefiks        " + "    \t " + "broj objava prefiksa ")
	print ""
	f.write("\n")

	broj_ASova=broj_ASova+1

	priv = AS
	priv.remove(AS[0])

	broj_prefiksa_AS=0
	broj_pojavljivanja_pref_AS=0
	for pref in priv:
		
		print "          \t " + str(pref[0]) + "     \t " + str(pref[1])
		f.write("\n          \t " + str(pref[0]) + "     \t " + str(pref[1]))
		broj_prefiksa_AS=broj_prefiksa_AS+1
		broj_pojavljivanja_pref_AS=broj_pojavljivanja_pref_AS + pref[1]
		broj_objava_pref_AS=broj_objava_pref_AS + pref[1]
		broj_parova_prefiks_AS=broj_parova_prefiks_AS+1

	print ""
	f.write("\n")
	print "          \t " + "ukupno prefiksa" + "    \t " + "ukupno objavljivanja"
	f.write("\n          \t " + "ukupno prefiksa" + "    \t " + "ukupno objavljivanja")
	print "          \t " + "za ovaj AS     " + "    \t " + "svih prefiksa za ovaj AS"
	f.write("\n          \t " + "za ovaj AS     " + "    \t " + "svih prefiksa za ovaj AS")
	print ""
	f.write("\n")
	print "          \t " + str(broj_prefiksa_AS) + "                  \t " + str(broj_pojavljivanja_pref_AS)
	f.write("\n          \t " + str(broj_prefiksa_AS) + "                  \t " + str(broj_pojavljivanja_pref_AS))
	
	print "\n"
	f.write("\n\n")
	print " --------------------------------- "
	f.write("\n --------------------------------- ")
	print "\n"
	f.write("\n\n")
			

print "\n"
f.write("\n\n")
print "Broj AS-ova>>>         	          \t " + str(broj_ASova)
f.write("\nBroj AS-ova>>>         	          \t " + str(broj_ASova))
print "Broj parova prefiks-AS>>>          \t " + str(broj_parova_prefiks_AS)
f.write("\nBroj parova prefiks-AS>>>          \t " + str(broj_parova_prefiks_AS))
print "Ukupan broj objava prefiks-AS>>>   \t " + str(broj_objava_pref_AS)
f.write("\nUkupan broj objava prefiks-AS>>>   \t " + str(broj_objava_pref_AS))
print ""
f.write("\n")
print "Prosjek prefiksa po AS-u>>>        \t " + str(float(broj_parova_prefiks_AS)/broj_ASova)
f.write("\nProsjek prefiksa po AS-u>>>        \t " + str(float(broj_parova_prefiks_AS)/broj_ASova))
print "Prosjek objava prefiksa po AS-u>>> \t " + str(float(broj_objava_pref_AS)/broj_ASova)
f.write("\nProsjek objava prefiksa po AS-u>>> \t " + str(float(broj_objava_pref_AS)/broj_ASova))
print "Prosjek objava i parova pref-AS>>> \t " + str(float(broj_objava_pref_AS)/broj_parova_prefiks_AS)
f.write("\nProsjek objava i parova pref-AS>>> \t " + str(float(broj_objava_pref_AS)/broj_parova_prefiks_AS))

print "\n"
f.write("\n\n\n")

f.close()

print "\n  Podaci su zapisani u datoteku " + dircur + '/ispisi/AS_prefiks_povezanost_ispis'




