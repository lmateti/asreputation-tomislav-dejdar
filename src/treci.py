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
import klase


dircur = os.getcwd()
if (len(sys.argv)>=2):
	d=BGPDump((dircur+ "/dumpovi/" +sys.argv[1]))
else:
	d=BGPDump((dircur + '/dumpovi/proba'))

lista_ann=[]

for mrth,bgph,bgpm in d:

	y=[]
	for el in bgpm.data.attributes:			#od svih atributa u pojedinom updateu
		if el.type==2:				# type=2 znaci da je atribut AS path
			as_double = 0
			for seg in el.data.segments:
       				for AS in seg.path:
					if (as_double!=AS):
						y.append(klase.As(AS))
						as_double=AS

	if bgpm.data.announced:

		for ek in bgpm.data.announced:		
			
			lista_ann.append( klase.Ann_Prefix(socket.inet_ntoa(ek.prefix),ek.len, mrth.ts, y, socket.inet_ntoa(struct.pack('>L',bgph.src_ip))) )

brojac=0


for elem in lista_ann:

	if (elem.writestrprefix()=="62.182.36.0/23"):
		print "\n"
		print "source:  \t" + elem.retsource()
		brojac=brojac+1
		print elem.writetime()
		print elem.writestrprefix()
		print elem.writeaspath()
		elem.MakeLinkList()
		print elem.writelinklist()
		print "\n"
	

print brojac
		

if 1==0:
	l=x.writestrprefix()
	print l
	print x.writetime()

	#x.setpref( "1.1.1.2", 19)
	l=x.writestrprefix()
	print l

	print x.writeprefix()
	print x.writelenght()

	for it in y:
		print it.writeAS()

	#y=[]

	print x.writeaspath()

	w=AS_path_to_AS_link_list(y)

	k=""
	for el in w:
		k=el.writestrlink()
		print k

	print "\n\n\n\n\n"

	x.MakeLinkList()

	print x.writetime()
	print x.writestrprefix()
	print x.writeaspath()
	print x.writelinklist()
	


