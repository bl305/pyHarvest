#!/usr/bin/env python
# coding=utf-8

import xlrd
import re
import os
from pyHarvest_xmod_patternmatch import *

#mypath='c:\\test\\XLS\\'
#myfilename='test.xlsx'
#set verbosity
#-1 - no messages
#0 - tuple of results
#1 - summary information
#2 - basic information, positive info
#3 - detailed information, positive, negative
#4 - go crazy about it...
#verbosity=0

#sample USAGE:
#myworkbook=xls_open(path)
#mysheets=xls_list_sheets(myworkbook)
#for mysheet in mysheets:
#	global sheet
#	sheet=myworkbook.sheet_by_name(mysheet)
#	xls_search_string(pattern_ALL,sheet,1)
#OR
#import search_patterns
#xls_full_search(path,search_patterns.pattern_VISA)
#OR
#allresults=xls_full_search(mypath,myfilename)
#alen=len(allresults)
#for a1 in range(alen):
#	print allresults[a1]

#SAMPLE SIMPLE USAGE SEARCH
#allresults=xls_full_search(mypath,myfilename)
#if verbosity==0:
#	print allresults

def xls_open(mypath,verbosity=0):
	myworkbook=()
	try:
		#read current sheets only to memory: 
		#workbook = xlrd.open_workbook(mypath, on_demand = True
		myworkbook=xlrd.open_workbook(mypath)
	except Exception,e:
		if verbosity>0:
			print "[-] Exception",e
	
	return myworkbook
def xls_list_sheets(myworkbook):
	mysheet_names=xls_list_sheets(myworkbook)
	return mysheet_names
	
#reads data line-by-line into an array
def xls_print_lines(mysheet):
	for i in range(mysheet.nrows):
		r = mysheet.row(i)
		print r

#reads all cells one by one running through all cells with data`
def xls_print_all_cells(mysheet,verbosity):
	#read cell values: sheet.cell(<row>, <column>).value
	for x in range(mysheet.ncols):
		for y in range(mysheet.nrows):
			#detect empty cell:
			#print "Next: %s %s" % (y,x)
			try:
				if mysheet.cell(y, x).value == xlrd.empty_cell.value:
					if verbosity>3:
						print "%s %s: EMPTY" % (y,x)
				else:
					#some error handling based on the type of data read
					myvalue=mysheet.cell(y, x).value
					myprint=""
					if isinstance(myvalue,float):
						myprint=myvalue
					elif isinstance(myvalue,int):
						myprint=myvalue
					else:
						myunivalue=myvalue.encode('utf-8','ignore')
						myprint=myunivalue
					print "%s %s: %s" % (y,x,myprint)
			except IndexError:
				print "%s %s: SKIPPED INDEX ERROR" % (y,x)
				
#reads all data into a matrix
def xls_read_all_cells_matrix(mysheet):
	data = [] #make a data store
	for j in xrange(sheet.nrows):
		data.append(sheet.row_values(j)) #drop all the values in the rows into data
	return data


#lists all the sheets in the workbook
def xls_list_sheets(myworkbook,verbosity):
	#print sheet statistics:
	for n, s in enumerate(myworkbook.sheets()):           
		if verbosity>1:
			print "[+] Sheet %d is called %s and has %d columns and %d rows" % (n, s.name, s.ncols, s.nrows)
	#sheet names in a tuple:
	sheet_names=myworkbook.sheet_names()
	return sheet_names
		
def xls_search_string_tuple_brief(mysheet,verbosity):
	results=()
	for y in xrange(sheet.nrows):
		for x in xrange(sheet.ncols):
			try:
				if mysheet.cell(y, x).value == xlrd.empty_cell.value:
					pass
					#print "%s %s: EMPTY" % (y,x)
				else:
					#some error handling based on the type of data read
					myvalue=mysheet.cell(y, x).value
					myprint=""
					if isinstance(myvalue,float):
						myprint=myvalue
						
					elif isinstance(myvalue,int):
						myprint=str(myvalue)
						myregex=find_pattern(myprint)
						if myregex:
							#print "[+] Found ASCII string \"%s\" in Sheet: \"%s\" at position: row:%s col:%s"%(myunivalue,sheet.name,y,x)
							#results+=(myregex[0]+(sheet.name,)+(y+1,)+(x,)),
							results+=(myregex[0]+(y+1,)+(x,)),

					else:
						myunivalue=myvalue.encode('utf-8','ignore')
						myprint=myunivalue
						myregex=find_pattern(myprint)
						if myregex:
							#print "[+] Found (utf-8) string \"%s\" in Sheet: \"%s\" at position: row:%s col:%s"%(myunivalue,sheet.name,y,x)
							#results+=(myregex[0]+(sheet.name,)+(y+1,)+(x,)),
							results+=(myregex[0]+(y+1,)+(x,)),

					#print "%s %s: %s" % (y,x,myprint)
			except IndexError:
				pass
				#print "%s %s: SKIPPED INDEX ERROR" % (y,x)
	if results:
		results=(results+(sheet.name,)),
	return results

def xls_search_string_tuple(mypath,myfile,mysheet,verbosity):
	results=()
	for y in xrange(sheet.nrows):
		for x in xrange(sheet.ncols):
			try:
				if mysheet.cell(y, x).value == xlrd.empty_cell.value:
					pass
					#print "%s %s: EMPTY" % (y,x)
				else:
					#some error handling based on the type of data read
					myvalue=mysheet.cell(y, x).value
					myprint=""
					if isinstance(myvalue,float):
						myprint=myvalue
						
					elif isinstance(myvalue,int):
						myprint=str(myvalue)
						myregex=find_pattern(myprint)
						if myregex:
							#print "[+] Found ASCII string \"%s\" in Sheet: \"%s\" at position: row:%s col:%s"%(myunivalue,sheet.name,y,x)
							#results+=(myregex[0]+(sheet.name,)+(y+1,)+(x,)),
							coord="%d:%d:%s"%(y+1,x,sheet.name)
							results+=(unicode(myregex[0][0]),unicode(myregex[0][1]),unicode(myregex[0][2]),unicode(coord),unicode(mypath),unicode(myfile)),

					else:
						myunivalue=myvalue.encode('utf-8','ignore')
						myprint=myunivalue
						myregex=find_pattern(myprint)
						if myregex:
							#print "[+] Found (utf-8) string \"%s\" in Sheet: \"%s\" at position: row:%s col:%s"%(myunivalue,sheet.name,y,x)
							#results+=(myregex[0]+(sheet.name,)+(y+1,)+(x,)),
							coord="%d:%d:%s"%(y+1,x,sheet.name)
							results+=(unicode(myregex[0][0]),unicode(myregex[0][1]),unicode(myregex[0][2]),unicode(coord),unicode(mypath),unicode(myfile)),

					#print "%s %s: %s" % (y,x,myprint)
			except IndexError:
				pass
				#print "%s %s: SKIPPED INDEX ERROR" % (y,x)
	return results

def xls_search_string_list(apath,averbosity=0):
	myinput=xls_full_search_tuple(apath,averbosity)
	result=""
	for i1 in range(len(myinput)):
		result+="%s\t%s\t%s\t%s\t%s\t%s\n"%(unicode(myinput[i1][0]),unicode(myinput[i1][1]),unicode(myinput[i1][2]),unicode(myinput[i1][3]),myinput[i1][4],myinput[i1][5])
	return result
	
def xls_full_search_tuple_brief(fullpath,verbosity=0):
	path=os.path.dirname(fullpath)
	filename=os.path.basename(fullpath)
	fresults=()
	myworkbook=xls_open(path+"\\"+filename,verbosity)
	if myworkbook<>():
		mysheets=xls_list_sheets(myworkbook,verbosity)
		for mysheet in mysheets:
			global sheet
			sheet=myworkbook.sheet_by_name(mysheet)
			if verbosity>2:
				print "[+] Sheet:",mysheet
			fresults+=xls_search_string_tuple_brief(sheet,verbosity)
		fresults+=(path,filename,),
	return fresults

	
def xls_full_search_tuple(fullpath,verbosity=0):
	path=os.path.dirname(fullpath)
	filename=os.path.basename(fullpath)
	fresults=()
	myworkbook=xls_open(path+"\\"+filename,verbosity)
	if myworkbook<>():
		mysheets=xls_list_sheets(myworkbook,verbosity)
		for mysheet in mysheets:
			global sheet
			sheet=myworkbook.sheet_by_name(mysheet)
			if verbosity>2:
				print "[+] Sheet:",mysheet
			fresults+=xls_search_string_tuple(path,filename,sheet,verbosity)
	return fresults

def xls_full_search_list(fullpath,verbosity=0):
	path=os.path.dirname(fullpath)
	filename=os.path.basename(fullpath)
	fresults=""
	myworkbook=xls_open(path+"\\"+filename,verbosity)
	if myworkbook<>():
		mysheets=xls_list_sheets(myworkbook,verbosity)
		for mysheet in mysheets:
			global sheet
			sheet=myworkbook.sheet_by_name(mysheet)
			if verbosity>2:
				print "[+] Sheet:",mysheet
			fresults+=xls_search_string_list(fullpath,verbosity)
	return fresults

#allresults=xls_full_search(mypath,myfilename)
#if verbosity==0:
#	print allresults