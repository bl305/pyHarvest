#!/usr/bin/env python
# coding=utf-8


from ftplib import FTP
from datetime import datetime
import time
import re
import os
import errno

#templates:
#IIS MS-DOS default
#11-01-15  05:11AM       <DIR>          Level1
#10-30-15  12:38PM                   12 Level2.txt
#10-30-15  12:38PM       <DIR>          Level2_2
#10-30-15  12:44PM       <DIR>          x
#maybe:^(\d{2}-\d{2}-\d{2})\s+(\d{2}:\d{2}(A|P)M)\s+(<DIR>)*\s+(\d*)\s+(\S+)

#IIS-UNIX default
#'-rwxrwxrwx   1 owner    group              12 Oct 30 12:38 Level2.txt'

#FTP PARAMETERS
#	#domain name or server ip:
#	#ftp = FTP('ftp.fau.de')
#	FTPserver='ftp.au.debian.org'
#	FTPdir='/pub/linux/debian/doc/'
#
#	#myftpserver='192.168.178.182'
#	#myftpdir='/'
#	FTPusername="anonymous"
#	FTPpassword="anony@mo.us"
#
#	#limit to pull files smaller than this
#	#http://www.whatsabyte.com/P1/byteconverter.htm
#	FTPflimit_1K=1024
#	FTPflimit_1M=1048576
#	FTPflimit_1GB=1073741824
#	#flimit_max:9223372036854775807
#	FTPflimit=FTPflimit_1K*1
#	#output directpry path
#	#current dir:
#	#outdir=os.path.realpath('.')
#	FTPoutdir="./DataGathered/FTP"
#
#	FTPskiplist=('/dev','/bin','/opt','initrd.img','vmlinuz')
#
#	FTPdownloadfiles=0
#	FTPcreatedirs=0

#http://code.activestate.com/recipes/499334-remove-ftp-directory-walk-equivalent/
def parse_dir_line_linux(ftp,top,myskiplist1):
	##################################################################################################
	#'drwxr-xr-x   5 ftpfau   ftpfau       4096 Sep 12  2013 aptosid'
	#'drwxrwxr-x 180 ftpfau   ftpfau       4096 Oct 27 17:14 apache'
	#sline=" ".join(line.split())
	#ssline=sline.split(' ')
	if top in myskiplist1:
		print "[+] Skipping dir: ",top
		return (),(),()
	dirs, nondirs = [], []
	data=[]
	datalen=len(data)
	ftp.dir(data.append)
	if datalen<len(data):
		#print "[+] New content"
		for line in data:
			ssline = line.split(None, 8)
		
			if len(ssline) < 6:
				print >> sys.stderr, 'Warning: Error reading short line', line
				pass#continue

			# Get the filename.
			filename = ssline[-1].lstrip()
			# Get the link target, if the file is a symlink.
			extra = None
			i = filename.find(" -> ")
			if i >= 0:
				# ssline[0] had better start with 'l'...
				extra = filename[i+4:]
				filename = filename[:i]
			if filename in ('.', '..','0'):
				pass#continue
			mysomething=ssline[1]
			myuser=ssline[2]
			mygroup=ssline[3]
			
			# Get the file size.
			size = int(ssline[4])

			# Get the date.
			year = datetime.today().year
			_calmonths = dict( (x, i+1) for i, x in
				   enumerate(('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
							  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')) )

			month = _calmonths[ssline[5]]
			day = int(ssline[6])
			mo = re.match('(\d+):(\d+)', ssline[7])
			if mo:
				hour, min = map(int, mo.groups())
			else:
				mo = re.match('(\d\d\d\d)', ssline[7])
				if mo:
					year = int(mo.group(1))
					hour, min = 0, 0
				else:
					raise ValueError("Could not parse time/year in line: '%s'" % line)
			dt = datetime(year, month, day, hour, min)
			mtime = time.mktime(dt.timetuple())
			mytime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
			# Get the type and permission.
			permission = ssline[0]
			filetype=""
			if permission[0] == '-':
				filetype="f"
			elif permission[0] == 'd':
				filetype="d"
			elif permission[0] == 'l':
				filetype="l"
			else:
				filetype="X"
			
			entry = (filename, permission, mysomething, myuser, mygroup, size, mytime, top, filetype, extra)
			if permission[0] == 'd':
				dirs.append(entry)
			else:
				nondirs.append(entry)
					
			#print "%s;%s;%s;%s;%s;%s;%s"%(permission,ssline[1],myuser,mygroup,size,dt,filename)
		#print "Dirs: ",dirs
		#print "Non-Dirs: ",nondirs
		return entry,dirs,nondirs

	else:
		print "[-] Empty dir: ",top
		return (),(),()

def ftpwalk_linux(ftp, top, myskiplist, topdown=True, onerror=None):
	"""
	Generator yields tuples of (root, dirs, nondirs).
	"""
	# Make the FTP object's current directory to the top dir.
	try:
		ftp.cwd(top)
	except:
		pass

	# We may not have read permission for top, in which case we can't
	# get a list of the files the directory contains.  os.path.walk
	# always suppressed the exception then, rather than blow up for a
	# minor reason when (say) a thousand readable directories are still
	# left to visit.  That logic is copied here.
	try:
		tmp,dirs,nondirs = parse_dir_line_linux(ftp,top,myskiplist)
	except os.error, err:
		if onerror is not None:
			onerror(err)
		return

	if topdown:
		yield top, dirs, nondirs
	if tmp <> ():

		for entry in dirs:
			dname = entry[0]
			#OR path = posixpath.join(top, dname)
			#path=os.path.join(top, dname)
			path1="%s/%s"%(top, dname)
			path=path1.replace('//','/')
			if (entry[-1] is None): # not a link
				for x in ftpwalk_linux(ftp, path, myskiplist, topdown, onerror):
					yield x

	if not topdown:
		yield top, dirs, nondirs

def get_file(ftp,ftpserver,path,filename,aoutdir,averbosity=0):
	abspath1=aoutdir+"/"+ftpserver+"/"+path+"/"
	abspath=abspath1.replace('//','/')
	abspathfile1=abspath+"/"+filename
	abspathfile2=abspathfile1.replace('//','/')
	abspathfile=abspathfile2.replace('//','/')
	try:
		if not os.path.exists(abspath):
			os.makedirs(abspath)
			print "[+] Creating directory %s" % abspath
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise
		else:
			#print "[-] Directory already exist %s" % apath
			pass
	try:
		fhandle = open(abspathfile, 'wb')
		try:
			getthis1=path + "/" + filename
			getthis=getthis1.replace('//','/')
			if averbosity>0:
				print "[+] Getting file \"%s\" to \"%s\""%(getthis,abspathfile)
			ftp.retrbinary("RETR " + getthis ,fhandle.write)
			return abspathfile
		except:
			print "[-] Error getting file \"%s\" to \"%s\""%(getthis,abspathfile)
			fhandle.close()
	except:
		print "Local file coulnd't be generated...file naming restriction???",abspathfile


def prepare_dir(autdir,ftpserver,path,adir,averbosity=0):
	abspath1=aoutdir+"/"+ftpserver+"/"+path+"/"+adir
	abspath=abspath1.replace('//','/')
	try:
		os.makedirs(abspath)
		if averbosity>0:
			print "[+] Creating directory %s" % path
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise
		else:
			if averbosity>3:
				print "[-] Directory already exist? %s" % path
			pass
	else:
		print "[-] Directory create error ... perhaps:)"
		pass
	return abspath1

def ftp_main(aftpserver,aftpdir,ausername,apassword,aflimit,aoutdir,askiplist,adownloadfiles=0,acreatedirs=0,averbosity=0):

	if averbosity>0:
		FTPflimit_1K=1024
		FTPflimit_1M=1048576
		FTPflimit_1GB=1073741824
		print "Size limit to pull per file KB:%d MB:%d GB:%d"%(aflimit/FTPflimit_1K,aflimit/FTPflimit_1M,aflimit/FTPflimit_1GB)

	ftp = FTP(aftpserver)
	ftp.login(user=ausername, passwd = apassword)
	ftp.cwd(aftpdir)

	allitems=()
	for root, dirs, files in ftpwalk_linux(ftp,aftpdir,askiplist):
		for name in dirs:
			if acreatedirs==1:
				prepare_dir(aoutdir,aftpserver,name[7],name[0],averbosity)
			if averbosity>2:
				print "Dir: %s %s %s %s %s %s %s %s %s %s %s"%(aftpserver,name[0],name[1],name[2],name[3],name[4],name[5],name[6],name[7],name[8],aoutdir)
			allitems+=(aftpserver,name[7],name[0],name[8],name[5],'',name[1],name[5],'','','',name[6],name[3],name[4],name[2],'',aoutdir),
			pass

		for name in files:
			if ((name[5]<aflimit) and (name[0] not in askiplist) and (name[8]<>'l')):
				if averbosity>2:
					print "Dir: %s %s %s %s %s %s %s %s %s %s %s"%(aftpserver,name[0],name[1],name[2],name[3],name[4],name[5],name[6],name[7],name[8],aoutdir)
				if adownloadfiles==1:
					get_file(ftp,aftpserver,name[7],name[0],aoutdir,averbosity)
				allitems+=(aftpserver,name[7],name[0],name[8],name[5],'',name[1],name[5],'','','',name[6],name[3],name[4],name[2],'',aoutdir),
				pass
			pass
	ftp.quit()
	return allitems