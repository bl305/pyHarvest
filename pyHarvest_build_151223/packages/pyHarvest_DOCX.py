#!/usr/bin/env python
# coding=utf-8


import os
from pyHarvest_xmod_patternmatch import *
from docx import opendocx, getdocumenttext

#mypath='c:\\test\\xtest.docx'
#set verbosity
#-1 - no messages
#0 - tuple of results
#1 - summary information
#2 - basic information, positive info
#3 - detailed information, positive, negative
#4 - go crazy about it...
myverbosity=0

def to_unicode_or_bust(obj, encoding='utf-8'):
	if isinstance(obj, basestring):
		if not isinstance(obj, unicode):
			obj = unicode(obj, encoding)
	return obj

def document_to_text(file_path):
	document = opendocx(file_path)
	paratextlist = getdocumenttext(document)
	newparatextlist = ()
	mycounter=0
	if paratextlist:
		for paratext in paratextlist:
			newparatextlist+=(paratext,mycounter),
			mycounter+=1
	return newparatextlist

def docx_full_search_tuple(apath,verbosity=0):
	mytext=document_to_text(apath)
	matches=()
	mypath=os.path.dirname(apath)
	myfilename=os.path.basename(apath)
	if verbosity>0:
		print "[+] Reading file:",apath
	try:
		for c1 in range(len(mytext)):
			mymatch=find_pattern(mytext[c1][0])
			
			if mymatch:
				for i1 in range(len(mymatch)):
					if verbosity>1:
						print "[+] Match found!!",mymatch[i1]
					matches+=(unicode(mymatch[i1][0]),unicode(mymatch[i1][1]),unicode(mymatch[i1][2]),unicode(mytext[c1][1]),unicode(mypath),unicode(myfilename)),
					pass
	#					try:
	#						print line.encode('utf-8')
	#						print "JO:",e
	#					except:
	#						if verbosity>3:
	#							print "[-] Cannot print using encoding",e
	#						pass

	except Exception,e:
		#print e
		pass
	return matches

def docx_full_search_list(apath,averbosity=0):
	myinput=docx_full_search_tuple(apath,verbosity=averbosity)
#	print myinput
	result=""
	for i1 in range(len(myinput)):
		#print myinput[i1]
		result+="%s\t%s\%s\t%s\t%s\t%s\n"%(unicode(myinput[i1][0]),unicode(myinput[i1][1]),unicode(myinput[i1][2]),unicode(myinput[i1][3]),unicode(myinput[i1][4]),unicode(myinput[i1][5]))
	return result
	

#print document_to_text(mypath)
#res=docx_full_search_tuple(mypath)
#res=docx_full_search_list(mypath)
#print res