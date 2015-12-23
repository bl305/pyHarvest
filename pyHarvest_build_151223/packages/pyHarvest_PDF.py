#!/usr/bin/env python
# coding=utf-8

#https://automatetheboringstuff.com/chapter13/
import PyPDF2
import re
import os
from pyHarvest_xmod_patternmatch import *

def pdf_read(path,verbosity=0):
	pdfFileObj = open(path, 'rb')
	pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	for i in range(pdfReader.numPages):
		try:
			pageObj = pdfReader.getPage(i)
			if verbosity>3:
				print pageObj.extractText().encode('utf-8')
		except KeyError:
			if verbosity>2:
				print "[-] Page couldn't be read"

def pdf_full_search_tuple_brief(path,verbosity=0):
	if verbosity>3:
		print "Searching for pattern"
	matches=()
	pdfFileObj = open(path, 'rb')
	pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	if verbosity>1:
		print "[+] Num of Pages:",pdfReader.numPages
	for i in range(pdfReader.numPages):
		try:
			pageObj = pdfReader.getPage(i)
			pagenum=i+1
			mytext=pageObj.extractText()#.encode('utf-8')
			mymatch=find_pattern(mytext)
			if mymatch:
				if verbosity>1:
					print "[+] MATCH for pattern \"%s\" on page #%d !!!"%(mymatch[0],pagenum)
				
				matches+=(mymatch+(pagenum,)),
		except KeyError:
			if verbosity>2:
				print "[-] Page couldn't be read: page #%d"%(i+1)
	if matches:
		tresult=matches
		tresult+=(os.path.dirname(path),os.path.basename(path)),
		return tresult

def pdf_full_search_tuple(apath,verbosity=0):
	if verbosity>3:
		print "Searching for pattern"
	matches=()
	mypath=os.path.dirname(apath)
	myfilename=os.path.basename(apath)

	pdfFileObj = open(apath, 'rb')
	pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	if verbosity>1:
		print "[+] Num of Pages:",pdfReader.numPages
	for i in range(pdfReader.numPages):
		try:
			pageObj = pdfReader.getPage(i)
			pagenum=i+1
			mytext=pageObj.extractText()#.encode('utf-8')
			mymatch=find_pattern(mytext)
			if mymatch:
				for i1 in range(len(mymatch)):
					if verbosity>1:
						print "[+] MATCH for pattern \"%s\" on page #%d !!!"%(mymatch[i1],pagenum)
					matches+=(mymatch[i1][0],mymatch[i1][1],mymatch[i1][2],unicode(pagenum),mypath,myfilename),
		except KeyError:
			if verbosity>2:
				print "[-] Page couldn't be read: page #%d"%(i+1)
	return matches

def pdf_full_search_list(apath,averbosity=0):
	myinput=pdf_full_search_tuple(apath,verbosity=averbosity)
#	print myinput
	result=""
	for i1 in range(len(myinput)):
		#print myinput[i1]
		result+="%s\t%s\t%s\t%s\t%s\t%s\n"%(unicode(myinput[i1][0]),unicode(myinput[i1][1]),unicode(myinput[i1][2]),unicode(myinput[i1][3]),unicode(myinput[i1][4]),unicode(myinput[i1][5]))
	return result

#mypath= 'c:\\test\\ztest.pdf'

#pdf_read(mypath)
#pdf_full_search(mypath)