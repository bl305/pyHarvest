#!/usr/bin/env python
# coding=utf-8

import chardet
import codecs
import re
import os
from pyHarvest_xmod_patternmatch import *


mypath=r'c:\test\FileEncoding\normal.txt'

#set verbosity
#-1 - no messages
#0 - tuple of results
#1 - summary information
#2 - basic information, positive info
#3 - detailed information, positive, negative
#4 - go crazy about it...
myverbosity=0

#max number of encoders to try - which seem to be a good one for reading
mymaxencode=0

#not used....
def to_unicode_or_bust(obj, encoding='utf-8'):
	if isinstance(obj, basestring):
		if not isinstance(obj, unicode):
			obj = unicode(obj, encoding)
	return obj

#GOOD:
def txt_get_all_encodings():
	import pkgutil
	import encodings

	false_positives = set(["aliases"])

	found = set(name for imp, name, ispkg in pkgutil.iter_modules(encodings.__path__) if not ispkg)
	found.difference_update(false_positives)

	#some default limited lists:
	#encodings = ['utf-8', 'windows-1250', 'windows-1252']
	#encodings = ['big5', 'big5hkscs', 'cp950', 'gb2312', 'gbk',
	#           'gb18030', 'hz', 'iso2022_jp_2', 'utf_16',
	#          'utf_16_be', 'utf_16_le', 'utf_8', 'utf_8_sig']
	return found 

#not really good
def txt_get_all_encodings_aliases():
	from encodings.aliases import aliases
	return aliases.keys()

#not really good
def txt_get_all_encodings_values():
	from encodings.aliases import aliases
	return aliases.values()

def txt_full_search_tuple_brief(path,maxencode=10,verbosity=0):
	encodings=txt_get_all_encodings()
	goodencodings=()
	matches=()
	maxencodecounter=0
	if verbosity>0:
		print "[+] Reading file:",path
	for e in encodings:
		if (maxencodecounter<maxencode) or (maxencode==0):
			if verbosity>3:
				print "[+] Current Encoding:%d, Max Encoding:%d"%(maxencodecounter,maxencode)
			try:
				if verbosity>1:
					print "[+] Testing encoding:",e
				fh = codecs.open(path, 'r', encoding=e)
				line=""

				try:
					line=fh.read()
					goodencodings+=(e,)
					maxencodecounter+=1
					#print "Encode:",e
					#match works regardless of unicode printing...doesn't throw an error that bad...but not good for big and simple unicode
					mymatch=find_pattern(line)
					if mymatch:
						if verbosity>1:
							print "[+] Match found!!",e,mymatch[0]
						mymatch+=(e,)
						matches+=(mymatch)
						pass
#					try:
#						print line.encode('utf-8')
#						print "Error:",e
#					except:
#						if verbosity>3:
#							print "[-] Cannot print using encoding",e
#						pass
				except:
					pass

				fh.close()
			except UnicodeDecodeError:
				pass
			except UnicodeError:
				pass
			else:
				pass#try all options
				#break #or stop at first, that might be good, might not...
	if matches:
		tresult=matches
		tresult+=(os.path.dirname(path),os.path.basename(path)),
		return tresult

def txt_full_search_tuple(apath,maxencode=10,verbosity=0):
	encodings=txt_get_all_encodings()
	goodencodings=()
	matches=()
	mypath=os.path.dirname(apath)
	myfilename=os.path.basename(apath)
	maxencodecounter=0
	if verbosity>0:
		print "[+] Reading file:",apath
	for e in encodings:
		if (maxencodecounter<maxencode) or (maxencode==0):
			if verbosity>3:
				print "[+] Current Encoding:%d, Max Encoding:%d"%(maxencodecounter,maxencode)
			try:
				if verbosity>1:
					print "[+] Testing encoding:",e
				fh = codecs.open(apath, 'r', encoding=e)
				line=""

				try:
					line=fh.read()
					goodencodings+=(e,)
					maxencodecounter+=1
					#print "Encode:",e
					#match works regardless of unicode printing...doesn't throw an error that bad...but not good for big and simple unicode
					mymatch=find_pattern(line)
					if mymatch:
						for i1 in range(len(mymatch)):
							#print "[+] Match found!!",e,mymatch[i1]
							if verbosity>1:
									print "[+] Match found!!",e,mymatch[i1]
							matches+=(unicode(mymatch[i1][0]),unicode(mymatch[i1][1]),unicode(mymatch[i1][2]),unicode(e),unicode(mypath),unicode(myfilename)),
							pass
		#					try:
		#						print line.encode('utf-8')
		#						print "JO:",e
		#					except:
		#						if verbosity>3:
		#							print "[-] Cannot print using encoding",e
		#						pass
				except:
					pass

				fh.close()
			except UnicodeDecodeError:
				pass
			except UnicodeError:
				pass
			else:
				pass#try all options
				#break #or stop at first, that might be good, might not...
	return matches

def txt_full_search_list(apath,amaxencode=10,averbosity=0):
	myinput=txt_full_search_tuple(apath,maxencode=amaxencode,verbosity=averbosity)
#	print myinput
	result=""
	for i1 in range(len(myinput)):
		#print myinput[i1]
		result+="%s\t%s\%s\t%s\t%s\t%s\n"%(unicode(myinput[i1][0]),unicode(myinput[i1][1]),unicode(myinput[i1][2]),unicode(myinput[i1][3]),unicode(myinput[i1][4]),unicode(myinput[i1][5]))
	return result

		
#if myverbosity>=0:
#	print txt_full_search_tuple_brief(mypath,maxencode=mymaxencode,verbosity=myverbosity)