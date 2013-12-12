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


#temp = socket.inet_ntoa(ek.prefix)+"/"+str(ek.len)


class Prefix:

	prefix = '0.0.0.0'
	lenght = 0
	
	# def __init__(self, pack_pref):
	#	self.prefix = socket.inet_ntoa(pack_pref.prefix)
	#	self.lenght = pack_pref.len

	def __init__(self, pref, lenght):			#konstruktor Prefix (str prefiks, int duljina)
		self.prefix = pref
		self.lenght = lenght

	def writestrprefix(self):				#vraca srting prefiks u formatu prefix/duljina
		return socket.inet_ntoa(self.prefix)+"/"+str(self.lenght)

	def writeprefix(self):					#vraca string prefiks
		return self.prefix

	def writelenght(self):					#vraca integer duljinu prefiksa
		return self.lenght

	def setpref(self, pref, lenght):			#postavlja prefiks (str prefiks, int duljina)
		self.prefix = pref
		self.lenght=lenght


class As:				#osnovna klasa za AS

	AS = 1				#int broj AS-a

	def __init__(self, AS):		#prima int broj AS-a
		self.AS = AS

	def writeAS(self):		#vraca int broj AS-a
		return self.AS

	def writestrAS(self):		#vraca str broj AS-a
		return str(self.AS)

class As_Rep_Inc(As):

	rep_inc = 0

	def __init__(self, AS):		#prima int broj AS-a
		self.AS = AS
		rep_inc = 0


class As_link:				#klasa za vezu dva AS-a

	left = As(1)			#instance klase As
	right = As(2)

	def __init__(self, left, right):	#konstruktor prima instance klase As
		self.left = left
		self.right = right

	def writestrlink(self):
		return self.left.writestrAS() + " " + self.right.writestrAS()
	
def AS_path_to_AS_link_list(list_as):		#argument je lista instanci As

	ll=[]
	l=As(0)
	r=As(1)
	brojac=0
	kraj=len(list_as)-1
	
	for el in list_as:
		if brojac==0:
			r=el
			brojac=brojac+1
		elif brojac<kraj:
			l=r
			r=el
			ll.append(As_link(l,r))
			brojac=brojac+1
		elif brojac==kraj:
			l=r
			r=el
			ll.append(As_link(l,r))
			break
		
		
	return ll		#vraca listu instanci As_link

def AddInc(lista_rep, lista_rep_inc, lista_inc):

	lista_tezina=[]

	for elem in lista_inc:
		pronadjeno=0
		for el in lista_rep:
			if elem.AS==el.AS:
				lista_tezina.append(As_Rep_Inc(elem.AS))
				lista_tezina[len(lista_tezina)-1].rep_inc=el.rep_inc
				pronadjeno=1
				break
		if pronadjeno==0:
			lista_tezina.append(As_Rep_Inc(elem.AS))
			lista_tezina[len(lista_tezina)-1].rep_inc=1

	

	if 1==0:
		for elem in lista_inc:	
			pojav=0
			for el in lista_rep_inc:			
				if elem.AS==el.AS:
					el.rep_inc=el.rep_inc+elem.rep_inc
					pojav=1
					break
			if pojav==0:
				lista_rep_inc.append(As_Rep_Inc(elem.AS))
				lista_rep_inc[len(lista_rep_inc)-1].rep_inc=elem.rep_inc

	return lista_rep_inc

		


class Ann_Prefix(Prefix):

	time = 1		#vrijeme postavljanja ovog prefiksa
	as_path = [1]		#popunjava se instancama klase As / put po AS-ovima za ovaj prefiks
	link_list = []		#lista linkova izmedju AS-ova na ovom putu
	source = ""

	def __init__(self, pref, lenght, time, list_as, source):	#konstruktor Ann_Prefix (str prefiks, int duljina, int time, lista AS-ova iz patha)
		self.prefix = pref
		self.lenght = lenght
		self.time = time
		self.as_path = list_as
		self.source=source
	
	def writetime(self):				#vraca string vrijeme postavljanja
		return time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime(self.time))

	def writeaspath(self):				#vraca string AS_path
		priv = ""
		for el in self.as_path:
			priv = priv + el.writestrAS() + ' '
		priv = priv[:-1]
		return priv

	def MakeLinkList(self):		#iz AS_patha stvara listu pojedinih veza izmedju AS-ova na tom putu

		self.link_list=AS_path_to_AS_link_list(self.as_path)

	def writelinklist(self):	#priprema za ispis listu AS-AS veza
		
		k=""
		for el in self.link_list:
			k = k + el.writestrlink() + "\n"
		return k

	def retsource(self):
		return self.source

def ReturnIndexAnn(list_ann, pref, lenght):	#vraca indeks trazenog prefiksa iz liste oglasenih prefiksa / lista instanci Ann_Prefix / ako nije pronadjen, vraca -1

	brojac = 0	
	for elem in list_ann:
		if elem.lenght==lenght:
			if elem.prefix==pref:
				return brojac
		brojac=brojac+1
	return -1

def ReturnASChanged(lista1, lista2):	#funkcija prima 2 liste popunjene instancama AS_link

	lista_nova=[]
	pojavl=0
	pojavr=0
	pojav=0

	for elem in lista1:
		pojavl=0
		pojavr=0
		for el in lista_nova:

			if elem.left.AS==el.AS:
				pojavl=1
			if elem.right.AS==el.AS:
				pojavr=1
		if pojavl==0:
			lista_nova.append(As_Rep_Inc(elem.left.AS))
			lista_nova[len(lista_nova)-1].rep_inc=0
		if pojavr==0:
			lista_nova.append(As_Rep_Inc(elem.right.AS))
			lista_nova[len(lista_nova)-1].rep_inc=0

	for elem in lista2:
		pojavl=0
		pojavr=0
		for el in lista_nova:

			if elem.left.AS==el.AS:
				pojavl=1
			if elem.right.AS==el.AS:
				pojavr=1
		if pojavl==0:
			lista_nova.append(As_Rep_Inc(elem.left.AS))
			lista_nova[len(lista_nova)-1].rep_inc=0
		if pojavr==0:
			lista_nova.append(As_Rep_Inc(elem.right.AS))
			lista_nova[len(lista_nova)-1].rep_inc=0

	for elem in lista1:
		pojav=0
		for ek in lista2:
			if elem.left.AS==ek.left.AS:
				if elem.right.AS==ek.right.AS:
					pojav=1
		if pojav==0:
						
			for el in lista_nova:
				if el.AS==elem.left.AS:
					el.rep_inc=el.rep_inc+1
				elif el.AS==elem.right.AS:
					el.rep_inc=el.rep_inc+1



	return lista_nova	#vraca listu parova [ [instanca As, broj izgubljenih linkova], ... ]




# ------------------------------------------------------------------------------------------------------------
		
if 1==0:

	l1 = []
	l1.append(As_link(As(1),As(2)))
	l1.append(As_link(As(2),As(3)))
	l1.append(As_link(As(3),As(4)))
	l1.append(As_link(As(4),As(5)))
	l1.append(As_link(As(5),As(13)))
	l1.append(As_link(As(13),As(14)))

	l2 = []
	l2.append(As_link(As(7),As(8)))
	l2.append(As_link(As(8),As(9)))
	l2.append(As_link(As(9),As(4)))
	l2.append(As_link(As(4),As(5)))
	l2.append(As_link(As(5),As(18)))


	print "\n\n"

	for ek in l1:

		print ek.writestrlink()

	print "\n\n"

	for ek in l2:

		print ek.writestrlink()

	print "\n\n"

	l3 = ReturnASChanged(l1, l2)

	for ek in l3:

		print "   " + ek[0].writestrAS() + "    \t " + str(ek[1])

	
if 1==0:

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
							y.append(As(AS))
							as_double=AS

		if bgpm.data.announced:

			for ek in bgpm.data.announced:		
			
				lista_ann.append( Ann_Prefix(socket.inet_ntoa(ek.prefix),ek.len, mrth.ts, y, socket.inet_ntoa(struct.pack('>L',bgph.src_ip))) )


if 1==0:
	for elem in lista_ann:

		print "\n"
		print elem.writetime()
		print elem.writestrprefix()
		print elem.writeaspath()
		elem.MakeLinkList()
		print elem.writelinklist()
		print "\n"
	
			

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
	


