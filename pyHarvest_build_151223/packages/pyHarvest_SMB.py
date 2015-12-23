#!/usr/bin/env python
# coding=utf-8

####
#TODO
#skipdirs
#sizelimit
#permissions
####

from smb.SMBConnection import SMBConnection
import time
import os
import errno
import socket
#from datetime import datetime
#import re
#from StringIO import StringIO

def convert_to_unicode(string):

    if not isinstance(string, unicode):
        string = unicode(string, "utf-8")
    return string


#######PARAMETERS
#	SMBusername='user1'
#	SMBusername=convert_to_unicode(SMBusername)
#	#in main
#	#SMBpassword='Asdf1234'
#	#SMBpassword = raw_input('password:')
#	#SMBpassword=convert_to_unicode(SMBpassword)
#	#SMBremotesystem = 'FileServer'
#	SMBremotesystem = 'REMOTESERVER'
#	SMBremotesystem=convert_to_unicode(SMBremotesystem)
#	SMBremoteip = '127.0.0.1'
#	SMBremoteip=convert_to_unicode(SMBremoteip)
#	#SMBlocalsystem='LOCALHOSTNAME'
#	SMBlocalsystem = socket.gethostname()
#	SMBlocalsystem=convert_to_unicode(SMBlocalsystem)
#	#SMBdomain='WORKGROUP'
#	SMBmydomain=convert_to_unicode(SMBdomain)
#	SMBfileshare='TestShare'
#	SMBfileshare=convert_to_unicode(SMBfileshare)
#	SMBoutdir="./DataGathered/SMB/"
#	SMBoutdir=convert_to_unicode(SMBoutdir)
#	SMBtop="/"
#	SMBtop=convert_to_unicode(SMBtop)
#	SMBtop=os.path.normpath(SMBtop).replace('//','/')
#	#if you want to find all shares and use them set this to 1, else the myfileshare will be used
#	SMBgetshares=0
#
#	#create empty directories?
#	SMBcreateemptydirs=0
#
#	#download files?
#	SMBdownloadfiles=1
#
#	#set verbosity
#	#-1 - no messages
#	#0 - tuple of results
#	#1 - summary information
#	#2 - basic information, positive info
#	#3 - detailed information, positive, negative
#	#4 - go crazy about it...
#	SMBverbosity=1

def smb_connect(username,password,localsystem,remotesystem,remoteIP,domain,averbosity=0):
	try:
		if averbosity>=1:
			print '[+] Analyzing system: ', remotesystem
		# parameterize an smb connection with a system
		conn = SMBConnection(username,
			password,
			localsystem,
			remotesystem,
			domain,
			use_ntlm_v2=True,
#this kills it			sign_options=SMBConnection.SIGN_WHEN_SUPPORTED,
			is_direct_tcp=True)

		# establish the actual connection
		connected = conn.connect(remoteIP,445)

		if connected:
			if averbosity>=2:
				print "[+] Connected"
		else:
			if averbosity>=3:
				print "[-] Connection failed"
				exit(1)
		return conn
	except Exception, e:
		if averbosity>=3:
			print('[-] Can not access the system')
		if averbosity>=4:
			print('[-] Can not access the system'),e
		#exit(2)

#this doesn't work for some reason...
def smb_list_shares(conn,aremotesystem,averbosity=0):
	if averbosity>=2:
		print '[+] Shares on: ', aremotesystem
	try:
		Response = conn.listShares(timeout=30)  # obtain a list of shares
		
		#for i in range(len(Response)):  # iterate through the list of shares
		#	print Response[i].name
		return tuple(Response)
	except Exception, e:
		if averbosity>=3:
			print('[-] Can not list shares')
		if averbosity>=4:
			print('[-] Can not list shares'),e

def smb_list_subfolders(conn,aremotesystem,ashare,apath,averbosity=0):
	if averbosity>=2:
		print "[+] Listing subfolders in share:\"%s\" folder: \"%s\""%(ashare,apath)
	try:
		Response = conn.listPath(ashare,apath,timeout=30)
		
		for i in range(len(Response)):
			filename=Response[i].filename
			fileisdir=Response[i].isDirectory
			filetype=""
			filecreatetime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(Response[i].create_time))
			fileattributes=Response[i].file_attributes
			fileallocsize=Response[i].alloc_size
			filesize=Response[i].file_size
			isreadonly=Response[i].isReadOnly
			lastaccesstime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(Response[i].last_access_time))
			filelastattrchangetime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(Response[i].last_attr_change_time))
			filelastwritetime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(Response[i].last_write_time))
			if filename == ".":
				pass
			elif filename == "..":
				pass
			else:
				newpath=os.path.join(apath,filename)
				newpath=os.path.normpath(newpath).replace('//','/')
				if averbosity>=4:
					print newpath
				if fileisdir:
					#print "DIR: ",filename
					filetype="d"
					for i in smb_list_subfolders(conn,aremotesystem,ashare,newpath):
						yield i
				else:
					filetype="f"
					#print "FIL: ",filename
					pass
				newfile=(ashare,apath,filename,filetype,filesize,filecreatetime,fileattributes,fileallocsize,isreadonly,lastaccesstime,filelastattrchangetime,filelastwritetime)
				yield newfile
	except Exception,e:
		if averbosity>=3:
			print '[-] Can not access the resource %s%s'% (ashare,apath)
		if averbosity>=4:
			print '[-] Can not access the resource %s%s%s'% (ashare,apath,e)
		pass

def smb_get_file(conn, remotesystem,filename,aoutdir,averbosity=0):
	apath = os.path.join(aoutdir,remotesystem)
	abspath=apath+filename
	abspath = os.path.normpath(abspath).replace('//','/')
	xpath, xfilename = os.path.split(filename)
	localdir=apath+xpath
	mycounter1=0
	mycounter2=0
	try:
		if not os.path.exists(localdir):
			os.makedirs(localdir)
			mycounter1+=1
			#print "[+] Creating directory %s" % apath
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise
		else:
			#print "[-] Directory already exist %s" % apath
			pass
	try:
		try:
			if averbosity>=2:
				print "[+] Creating local file:",abspath
			temp_fh = open(abspath, 'wb')
		except:
			if averbosity>=3:
				"[-] Could not create local file",abspath

		try:
			if averbosity>=3:
				print "[+] Pulling %s"%(abspath)
			file_attributes, filesize = conn.retrieveFile(remotesystem, filename, temp_fh, timeout=30)
			mycounter2+=1
		except:
			if averbosity>=3:
				"[-] Could not retrieve file %s %s",(remotesystem, filename)
			
		temp_fh.close()
		if averbosity>=1:
			print "[+] Got file %s"%abspath
	except Exception,e:
		if averbosity>=3:
			print "[-] Could not create file: %s"%abspath
		if averbosity>=4:
			print "[-] Could not create file: %s %s"%(abspath,e)
	return mycounter1,mycounter2
		
def smb_prepare_dir(remotesystem,abspath):
	mycounter1=0
	try:
		if not os.path.exists(abspath):
			os.makedirs(abspath)
			mycounter1+=1
			#print "[+] Creating directory %s" % path
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise
		else:
			#print "[-] Directory already exist %s" % path
			pass
	return mycounter1

def smb_main(ausername,apassword,alocalsystem,aremotesystem,aremoteip,adomain,afileshare,atop,aoutdir,adownloadfiles=1,acreateemptydirs=0,agetshares=0,averbosity=0):

	if averbosity>=1:
		#print summary:
		print "Server             :",aremotesystem
		print "File Share         :",afileshare
		print "Skipped directories: TBD"
		print "Skipped files      : TBD"
		print "Maximum depth      : TBD"
		print "Max filesize       : TBD"


	myconn=smb_connect(ausername,apassword,alocalsystem,aremotesystem,aremoteip,adomain)
	#this will be populated based on the agetshares parameter
	shares=()
	if agetshares == 1:
		allshares = smb_list_shares(myconn,aremotesystem)
		for i1 in range(len(allshares)):
			shares+=(allshares[i1].name),
			if averbosity>=4:
				print "[+] Shares in server:",allshares[i1].name
	else:
		if averbosity>=4:
			print "[+] Shares in server:",fileshare
		shares=(afileshare),

	allitems=()
	fcount=0
	dcount=0
	dnum1=0
	fnum2=0
	dnum2=0

	for a1 in range(len(shares)):
		if averbosity>=4:
			print shares[a1]

		for i in smb_list_subfolders(myconn,aremotesystem,shares[a1],atop):
			item=os.path.join(aoutdir+"/"+i[0]+"/"+i[1],i[2])
			item=os.path.normpath(item).replace('//','/')
			fileitem=os.path.join(i[1],i[2]).replace('//','/')
			if i[3] == "d":
				dcount+=1
				if acreateemptydirs==1:
					dnum1+=smb_prepare_dir(aremotesystem,item)
				if averbosity>=4:
					print "DIR: %s"%item
			elif i[3] == "f":
				fcount+=1
				if averbosity>=4:
					print "FIL: %s %s"%(i[0],fileitem)
				if adownloadfiles==1:
					dnumTMP,fnumTMP=smb_get_file(myconn, i[0],fileitem,aoutdir)
					dnum2+=dnumTMP
					fnum2+=fnumTMP
				if averbosity>=4:
					print "(%s) %s%s%s (%s) (%s) (%s) (%s) (%s) (%s) (%s) (%s)"%(i[3],i[0],i[1],i[2],i[4],i[5],i[6],i[7],i[8],i[9],i[10],i[11])
			allitems+=(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9],i[10],i[11],'','','','',aoutdir),
			pass
	if averbosity==0:
		print allitems

	if averbosity>=1:
		print "Found %d directories and %d files"%(dcount,fcount)
		print "Created %d directories using directory downloader (absolute path)"%(dnum1)    
		print "Created %d directories (absolute path) and %d files (if existed, overwritten)"%(dnum2,fnum2)

	myconn.close()
	return allitems