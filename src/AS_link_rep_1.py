#!/usr/bin/env python

################################################
#	
#	
#	
#
#
#
#
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
import klase


lista_ann=[]		#lista objavljenih prefiksa s pripadajucim podacima
lista_rep=[]		#lista reputacija za AS-ove
lista_rep_inc=[]	#lista inkremenata reputacije

dircur = os.getcwd()
os.chdir(dircur + "/dumps2")
file_list = glob.glob("*.*")
file_list_brojac=0
#print file_list
file_list.sort()

dump_list=[]

for file_name in file_list:
	dump_list.append(BGPDump(file_name))

f = open(dircur + '/ispisi/peti', 'w')

#d=dump_list[0]


for d in dump_list:
	print "\n  Obradjujem datoteku " + file_list[file_list_brojac] + "\n"
	file_list_brojac=file_list_brojac+1

	for mrth,bgph,bgpm in d:

		as_temp=[]				#lista AS-ova u pojedinom Update-u
		index=-1
		for el in bgpm.data.attributes:			#od svih atributa u pojedinom updateu
			if el.type==2:				# type=2 znaci da je atribut AS path
				as_double = 0
				for seg in el.data.segments:
	       				for AS in seg.path:
						if (as_double!=int(AS)):
							as_temp.append(klase.As(int(AS)))	#u listu AS-ova upisuju se instance klase As
							as_double=int(AS)

		if bgpm.data.announced:

			for ek in bgpm.data.announced:		#gledamo sve prefikse iz tog Update-a
				#temp= socket.inet_ntoa(ek.prefix)+"/"+str(ek.len)
				index = klase.ReturnIndexAnn(lista_ann, ek.prefix, ek.len)			
			
				#prvo dodajemo na kraj liste novu instancu objavljenog prefiksa Ann_Prefix

				if index==-1:

					lista_ann.append( klase.Ann_Prefix(ek.prefix, ek.len, mrth.ts, as_temp, socket.inet_ntoa(struct.pack('>L',bgph.src_ip))) )
					lista_ann[len(lista_ann)-1].MakeLinkList()
					

				else:
					lista_ann.append( klase.Ann_Prefix(ek.prefix, ek.len, mrth.ts, as_temp, socket.inet_ntoa(struct.pack('>L',bgph.src_ip))) )
					lista_ann[len(lista_ann)-1].MakeLinkList()

					if lista_ann[index].writeaspath()!=lista_ann[len(lista_ann)-1].writeaspath():
					
						#sljedeci dio usporedjuje stari i novi put i trazi razlike

						lis1= lista_ann[index].link_list
						lis2= lista_ann[len(lista_ann)-1].link_list

						l5 = klase.ReturnASChanged(lis1, lis2)

						lista_rep_inc=klase.AddInc(lista_rep_inc, l5)

						f.write( "\n----------------------------------\n  Withdrawn by Announcement:\n")
						f.write("\n  Prefix:  \t " + lista_ann[index].writestrprefix())
						f.write("\n  AS-path  \t " + lista_ann[index].writeaspath() + "\n\n")
						f.write(lista_ann[index].writelinklist())

						f.write( "\n----------------------------------\n  Announced:\n")
						f.write("\n  Prefix:  \t " + lista_ann[len(lista_ann)-1].writestrprefix())
						f.write("\n  AS-path  \t " + lista_ann[len(lista_ann)-1].writeaspath() + "\n\n")
						f.write(lista_ann[len(lista_ann)-1].writelinklist())

						f.write("\n")
						for ek in l5:
							f.write("   " + ek[0].writestrAS() + "    \t " + str(ek[1]) + "\n")

					#sada izbrisi staru objavu prefiksa
					lista_ann.pop(index)

					#print str(len(lista_ann))
					#lista_ann.remove(lista_ann[index])



		if bgpm.data.withdrawn:

			for ek in bgpm.data.withdrawn:		#gledamo sve prefikse iz tog Update-a
				#temp= socket.inet_ntoa(ek.prefix)+"/"+str(ek.len)
				index = klase.ReturnIndexAnn(lista_ann, ek.prefix, ek.len)			
				
				if index!=-1:
					
					lis1= lista_ann[index].link_list
					lis2= []

					l5 = klase.ReturnASChanged(lis1, lis2)

					lista_rep_inc=klase.AddInc(lista_rep_inc, l5)

					f.write( "\n----------------------------------\n  Withdrawn:\n")
					f.write("\n  Prefix:  \t " + lista_ann[index].writestrprefix())
					f.write("\n  AS-path  \t " + lista_ann[index].writeaspath() + "\n\n")
					f.write(lista_ann[index].writelinklist())

					f.write("\n")
					for ek in l5:
						f.write("   " + ek[0].writestrAS() + "    \t " + str(ek[1]) + "\n")

					#sada izbrisi staru objavu prefiksa
					lista_ann.pop(index)
			


f.write("\n---------------------------")
f.write("\n---------------------------\n")

for elem in lista_rep_inc:

	f.write("  " + elem.writestrAS() + "     \t " + str(elem.rep_inc) + "\n")

print "  \n\n"
