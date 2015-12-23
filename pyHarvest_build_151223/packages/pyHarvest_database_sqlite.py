#!/usr/bin/env python
# coding=utf-8

import ast
import sqlite3
from datetime import datetime
#print "SQLite database binding version: " +sqlite3.version
#print "SQLite database library version: " + sqlite3.sqlite_version

#TBD: table references in insert_value functions
#TBD: FTP insert valu to parameterized insert: 	e.g. in Analysis

db_store="dbfiles\\"
#inputs:

Files_sqlite_file= db_store+'File_Listings_db.s3db'
Files_table_name = 'Files'
Files_create_script="CREATE TABLE %s (\
	ID INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,\
	P_SHARE TEXT NOT NULL,\
	P_PATH VARCHAR(255) NOT NULL,\
	P_FILE VARCHAR(255) NOT NULL,\
	P_TYPE CHAR(1) NOT NULL,\
	P_SIZE INTEGER,\
	P_CREATETIME CHAR(19),\
	P_ATTRIBUTES VARCHAR(12),\
	P_ALLOCSIZE INTEGER,\
	P_ISREADONLY VARCHAR(5),\
	P_LASTACCESSTIME CHAR(19),\
	P_LASTATTRCHANGE CHAR(19),\
	P_LASTWRITE CHAR(19),\
	P_GROUP VARCHAR(50),\
	P_USER VARCHAR(50),\
	P_X VARCHAR(50),\
	P_LOCALDIR VARCHAR(255),\
	P_AINDEX INTEGER,\
	RECORDDATE TEXT);"%Files_table_name
	
Analysis_sqlite_file = db_store+'Analysis_db.s3db'    # name of the sqlite database file
Analysis_table_name='Regex_Matches'
Analysis_create_script="CREATE TABLE %s (\
	ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,\
	P_Type VARCHAR(10) NULL,\
	P_Match_NAME VARCHAR(255) NULL,\
	P_Match_VALUE VARCHAR(255) NULL,\
	P_Match_REGEX VARCHAR(255) NULL,\
	P_ADDITIONAL VARCHAR(255) NULL,\
	P_Path VARCHAR(255) NULL,\
	P_File VARCHAR(255) NULL,\
	P_Findex INTEGER NULL,\
	RECORDDATE TEXT);"%Analysis_table_name

def str2tuple(strin):
	return ast.literal_eval(strin)

def tuple_parse(s):
    tuples = s.split('), ')
    out = []
    for x in tuples:
        a,b = x.strip('()').split(', ')
        out.append((float(a),float(b)))
    return out
	
def db_connect(sqlite_file, print_out=0):
	""" Make connection to an SQLite database file """
	if print_out==1:
		print "\nConnecting to ",sqlite_file
	conn = sqlite3.connect(sqlite_file)
	c = conn.cursor()
	return conn, c

def create_host_db(cursor,mycreate_script, print_out=True):
	try:
		if print_out:
			print "[+] Trying to create database", mycreate_script
		cursor.execute(mycreate_script)
		if print_out:
			print('[+] Database created')
	except sqlite3.OperationalError:
		print "[-] Error - CREATE failed - database exist?"
	return cursor

def total_rows(cursor, table_name, print_out=False):
    """ Returns the total number of rows in the database """
    cursor.execute('SELECT COUNT(*) FROM {}'.format(table_name))
    count = cursor.fetchall()
    if print_out:
        print('\n[+] Total rows in database: {}'.format(count[0][0]))
    return count[0][0]

def table_col_info(mycursor, table_name, print_out=False):
	""" 
		Returns a list of tuples with column informations:
		(id, name, type, notnull, default_value, primary_key)
	"""
	print "\n[+] Column information for table",table_name
	mycursor.execute('PRAGMA TABLE_INFO({})'.format(table_name))
	info = mycursor.fetchall()

	if print_out:
		print("\nColumn Info:\nID, Name, Type, NotNull, DefaultVal, PrimaryKey")
		for col in info:
			print(col)
	return info

def values_in_col(cursor, table_name, print_out=True):
    """ Returns a dictionary with columns as keys and the number of not-null 
        entries as associated values.
    """
    cursor.execute('PRAGMA TABLE_INFO({})'.format(table_name))
    info = cursor.fetchall()
    col_dict = dict()
    for col in info:
        col_dict[col[1]] = 0
    for col in col_dict:
        cursor.execute('SELECT ({0}) FROM {1} WHERE {0} IS NOT NULL'.format(col, table_name))
        # In my case this approach resulted in a better performance than using COUNT
        number_rows = len(cursor.fetchall())
        col_dict[col] = number_rows
    if print_out:
        print("\n[+] Number of entries per column:")
        for i in col_dict.items():
            print('{}: {}'.format(i[0], i[1]))
    return col_dict

def values_all_tuple(mycursor, table_name, print_out=True):
	""" Returns all values in a tuple.
	"""
	print("\n[+] Listing database contents as a tuple...")
	cursor1 = mycursor.execute("SELECT * from %s"%table_name)
	all_rows = cursor1.fetchall()
	if print_out:
		print('1):', all_rows)
	return tuple(all_rows)

def values_all(mycursor, table_name, print_out=True):
	""" Returns all values in a tuple.
	"""
	if print_out:
		print("\n[+] Listing database contents...")
	cursor1 = mycursor.execute("SELECT * from %s"%table_name)
	for row in cursor1:
		for i in range(len(row)):
			if print_out:
				print "%d = %s"%(i,row[i])
	if print_out:
		print "\n"
	return cursor1

def db_commit(myconn):
	myconn.commit()

def db_close(myconn,print_out=0):
	# Committing changes and closing the connection to the database file
	myconn.commit()
	if print_out==1:
		print "Commit successfull";
	myconn.close()	

def insert_db_file_values(cursor, t1, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, atime, print_out=True):
	try:
		if print_out:
			print('[+] Trying to insert values...')
		myquery="INSERT INTO %s (P_SHARE,P_PATH,P_FILE,P_TYPE,P_SIZE,P_CREATETIME,P_ATTRIBUTES,P_ALLOCSIZE,P_ISREADONLY,P_LASTACCESSTIME,P_LASTATTRCHANGE,P_LASTWRITE,P_GROUP,P_USER,P_X,P_LOCALDIR,P_AINDEX,RECORDDATE) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"%t1
		cursor.execute(myquery,(p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,atime))
	except sqlite3.IntegrityError:
		print "[-] Error - INSERT failed for row: (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" % (p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,mytime)

		
def insert_db_file_data(cursor, mytable, mydatain, print_out=True):
	mytime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	for mydata in mydatain:
		if mydata[3]=='f':
			#print "[+] Inserting file:",mydata
			insert_db_file_values(cursor, mytable, mydata[0], mydata[1],mydata[2],mydata[3],mydata[4],mydata[5],mydata[6],mydata[7],mydata[8],mydata[9],mydata[10],mydata[11],mydata[12],mydata[13],mydata[14],mydata[15],mydata[16], mytime, print_out)
			pass
		elif mydata[3]=='d':
			#print "[+] Inserting directory:",mydata
			insert_db_file_values(cursor, mytable, mydata[0], mydata[1]+"/"+mydata[2],'',mydata[3],mydata[4],mydata[5],mydata[6],mydata[7],mydata[8],mydata[9],mydata[10],mydata[11],mydata[12],mydata[13],mydata[14],mydata[15],mydata[16], mytime, print_out)
			pass
		else:
			print "Cannot identify if it is a file or directory!!!"
			pass
		
def create_db_file_and_fill_with_data(aFiles_sqlite_file,aFiles_create_script,datain,print_out=True):
	#CREATE FTP DATABASE:
	Filesconn, Filesc = db_connect(aFiles_sqlite_file)
	create_host_db(Filesconn, aFiles_create_script,print_out=True)
	
	#INSERT DATA INTO FTP DATABASE (from tuple)
	insert_ftp_data(Filesc,datain)
	db_commit(Filesconn)
	return Filesconn,Filesc

def insert_analysis_values(cursor, t1, p1, p2, p3, p4, p5, p6, p7 ,p8, atime,print_out=True):
	try:
		if print_out:
			print('[+] Trying to insert values...')
		p1=unicode(p1)
		p2=unicode(p2)
		p3=unicode(p3)
		p4=unicode(p4)
		p5=unicode(p5)
		p6=unicode(p6)
		p7=unicode(p7)
		p8=unicode(p8)
		myquery="INSERT INTO %s (P_Type,P_MATCH_NAME,P_MATCH_VALUE,P_MATCH_REGEX,P_ADDITIONAL,P_Path,P_File,P_Findex,RECORDDATE) VALUES (?,?,?,?,?,?,?,?,?)"%t1
		cursor.execute(myquery,(p1,p2,p3,p4,p5,p6,p7,p8,atime))
	except sqlite3.IntegrityError:
		print "[-] Error - INSERT failed for row: (%s,%s,%s,%s,%s,%s,%s,%s,%s)" % (p1,p2,p3,p4,p5,p6,p7,p8,atime)
		
def insert_analysis_data(cursor, mytable, mydatain, mytype, print_out=True):
	mytime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	for i1 in range(len(mydatain)):
		if print_out:
			print '[+] Trying to insert values...'
		#mytype
		mymatchname=mydatain[i1][0]
		mymatchvalue=mydatain[i1][1]
		mymatchregex=mydatain[i1][2]
		myadditional=mydatain[i1][3]
		mypath=mydatain[i1][4]
		myfile=mydatain[i1][5]
		myfindex=0
		#print "XXX",mytable, mytype, mymatchname,mymatchvalue,mymatchregex,myadditional,mypath,myfile,myfindex,mytime
		insert_analysis_values(cursor, mytable, mytype, mymatchname,mymatchvalue,mymatchregex,myadditional,mypath,myfile,myfindex,mytime, print_out=False)
		#print "X",mypath,myfile

def create_analysis_and_fill_with_data(datain,ftype,print_out=True):
	#CREATE ANALYSIS DATABASE:
	Analysisconn, Analysisc = db_connect(Analysis_sqlite_file)
	create_host_db(Analysisconn, Analysis_create_script,print_out=False)
	
	#INSERT DATA INTO ANALYSIS DATABASE (from tuple)
	insert_analysis_data(Analysisc,Analysis_table_name,datain,ftype)
	return Analysisconn,Analysisc


def tuple2csv(Analysisdata):
	if len(Analysisdata)>0:
		for i1 in range(len(Analysisdata)):
			print "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s"%(Analysisdata[i1][0],Analysisdata[i1][1],Analysisdata[i1][2],Analysisdata[i1][3],Analysisdata[i1][4],Analysisdata[i1][5],Analysisdata[i1][6],Analysisdata[i1][7],Analysisdata[i1][8],Analysisdata[i1][9])
			pass


SMB_data=(
(u'TestShare', u'\\l1\\l2a', u'testl2a.txt', 'f', 16, '2015-11-20 14:43:57', 32, 16, False, '2015-11-20 14:43:57', '2015-12-16 10:02:34', '2015-11-20 16:56:50', 'n/a', 'n/a', 'n/a', 'n/a', u'./DataGathered/SMB/'), 
(u'TestShare', u'\\l1', u'l2a', 'd', 0, '2015-11-20 14:43:48', 16, 0, False, '2015-11-20 14:43:57', '2015-11-20 14:43:57', '2015-11-20 14:43:57', 'n/a', 'n/a', 'n/a', 'n/a', u'./DataGathered/SMB/'), 
(u'TestShare', u'\\l1', u'l2b', 'd', 0, '2015-11-20 14:43:50', 16, 0, False, '2015-11-20 14:43:50', '2015-11-20 14:43:50', '2015-11-20 14:43:50','n/a', 'n/a', 'n/a', 'n/a', u'./DataGathered/SMB/'), 
(u'TestShare', u'\\', u'l1', 'd', 0, '2015-11-20 14:43:45', 16, 0, False, '2015-11-20 14:43:51', '2015-11-20 14:43:51', '2015-11-20 14:43:51', 'n/a', 'n/a', 'n/a', 'n/a', u'./DataGathered/SMB/'), 
(u'TestShare', u'\\', u'testlevel1a.txt', 'f', 12, '2015-11-20 14:44:06', 32, 16, False, '2015-11-20 14:44:06', '2015-12-16 10:02:34', '2015-11-20 16:57:09', 'n/a', 'n/a', 'n/a', 'n/a', u'./DataGathered/SMB/'), 
(u'TestShare', u'\\', u'x.txt', 'f', 8, '2015-11-23 16:09:22', 32, 8, False, '2015-11-23 16:09:22','2015-12-16 10:02:34', '2015-11-23 16:09:25', 'n/a', 'n/a', 'n/a', 'n/a', u'./DataGathered/SMB/')
)
			
FTP_data=(
('ftp.au.debian.org', '/pub/linux/debian/doc/', 'FAQ', 'd', 4096, '2015-05-01 00:00:00', 'drwxr-sr-x', 4096, 'n/a', 'n/a', 'n/a', 'n/a', '1005', '1005', '2', 'n/a', './DataGathered/FTP'), 
('ftp.au.debian.org', '/pub/linux/debian/doc/', 'dedication', 'd', 4096, '2009-02-14 00:00:00', 'drwxr-sr-x', 4096, 'n/a', 'n/a', 'n/a', 'n/a', '1005', '1005', '2', 'n/a', './DataGathered/FTP'), 
('ftp.au.debian.org', '/pub/linux/debian/doc/', '00-INDEX', 'f', 995, '2009-02-07 00:00:00', '-rw-r--r--', 995, 'n/a', 'n/a', 'n/a', 'n/a', '1005', '1005', '1', 'n/a', './DataGathered/FTP'), 
('ftp.au.debian.org', '/pub/linux/debian/doc/dedication', 'dedication-5.0.cs.txt', 'f', 972, '2009-02-13 00:00:00', '-rw-r--r--', 972, 'n/a', 'n/a', 'n/a', 'n/a', '1005', '1005', '1', 'n/a', './DataGathered/FTP'), 
('ftp.au.debian.org', '/pub/linux/debian/doc/dedication', 'dedication-5.0.lt.txt', 'f', 1008, '2009-02-13 00:00:00', '-rw-r--r--', 1008, 'n/a', 'n/a', 'n/a', 'n/a', '1005', '1005', '1', 'n/a', './DataGathered/FTP'), 
('ftp.au.debian.org', '/pub/linux/debian/doc/dedication', 'dedication-5.0.sk.txt', 'f', 942, '2009-02-13 00:00:00', '-rw-r--r--', 942, 'n/a', 'n/a', 'n/a', 'n/a', '1005', '1005', '1', 'n/a', './DataGathered/FTP'), 
('ftp.au.debian.org', '/pub/linux/debian/doc/dedication', 'dedication-5.0.sv.txt', 'f', 1012, '2009-02-13 00:00:00', '-rw-r--r--', 1012, 'n/a', 'n/a', 'n/a', 'n/a', '1005', '1005', '1', 'n/a', './DataGathered/FTP'), 
('ftp.au.debian.org', '/pub/linux/debian/doc/dedication', 'dedication-5.0.txt', 'f',984, '2009-02-06 00:00:00', '-rw-r--r--', 984, 'n/a', 'n/a', 'n/a', 'n/a', '1005', '1005', '1', 'n/a', './DataGathered/FTP')
)

#FTPdata=('16877', 'None', 'None', 'd', '2', u'1000', u'1001', '4096', 'None', '1447272840.0', 'None', u'/home/bali/Level1a/Level2a', u'Level3a'),('33156', 'None', 'None', 'f', '1', u'1000', u'1001', '6', 'None', '1447247700.0', 'None', u'/home/bali/Level1a', u'level2.txt'),
#FTPconn,FTPc=create_ftp_and_fill_with_data(FTPdata)
#PRINT DATABASE CONTENTS
#total_rows(FTPc, FTP_table_name, print_out=True)
#table_col_info(FTPc, FTP_table_name, print_out=True)
#values_in_col(FTPc, FTP_table_name, print_out=True) # slow on large data bases
#values_all_tuple(FTPc, FTP_table_name, print_out=True)
#values_all(FTPc, FTP_table_name, print_out=True)
#db_commit(FTPconn)
#db_close(FTPconn)

#TXT
TXT_data_brief=((u'900e3f2dd4efc9892793222d7a1cee4a', 'PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)'), 
 (u'AC905DD4AB2038E5F7EABEAE792AC41B', 'PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)'), 
 (u'password', 'pwd_password', u'(?i)password'), 
 (u'passw', 'pwd_passw', u'(?i)passw'), 'euc_jp', 
 (u'900e3f2dd4efc9892793222d7a1cee4a', 'PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)'), 
 (u'AC905DD4AB2038E5F7EABEAE792AC41B', 'PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)'), 
 (u'password', 'pwd_password', u'(?i)password'), 
 (u'passw', 'pwd_passw', u'(?i)passw'), 'cp932', 
 (u'900e3f2dd4efc9892793222d7a1cee4a', 'PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)'), 
 (u'AC905DD4AB2038E5F7EABEAE792AC41B', 'PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)'), 
 (u'password', 'pwd_password', u'(?i)password'), 
 (u'passw', 'pwd_passw', u'(?i)passw'), 'euc_jisx0213', 
 ('c:\\test\\TXT', 'normal.txt'))

((u'900e3f2dd4efc9892793222d7a1cee4a', 'PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)'), 
 (u'AC905DD4AB2038E5F7EABEAE792AC41B', 'PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)'), 
 (u'cf23df2207d99a74fbe169e3eba035e633b65d94', 'PWD_SHA1', u'\\b([a-f0-9]{40})\\b'), 
 (u'password', 'pwd_password', u'(?i)password'), (u'passw', 'pwd_passw', u'(?i)passw'), 'big5hkscs', 
 (u'900e3f2dd4efc9892793222d7a1cee4a', 'PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)'), 
 (u'AC905DD4AB2038E5F7EABEAE792AC41B', 'PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)'), 
 (u'cf23df2207d99a74fbe169e3eba035e633b65d94', 'PWD_SHA1', u'\\b([a-f0-9]{40})\\b'), 
 (u'password', 'pwd_password', u'(?i)password'), 
 (u'passw','pwd_passw', u'(?i)passw'), 'mac_romanian', 
 (u'900e3f2dd4efc9892793222d7a1cee4a', 'PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)'), 
 (u'AC905DD4AB2038E5F7EABEAE792AC41B','PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)'), 
 (u'cf23df2207d99a74fbe169e3eba035e633b65d94', 'PWD_SHA1', u'\\b([a-f0-9]{40})\\b'), 
 (u'password', 'pwd_password', u'(?i)password'), 
 (u'passw', 'pwd_passw', u'(?i)passw'), 'mbcs', 
 ('c:\\test\\TXT', 'unicode_utf8.txt'))

TXT_data_tuple=(
(u'900e3f2dd4efc9892793222d7a1cee4a', u'PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)', u'euc_jp', u'c:\\test\\TXT', u'normal.txt'), 
(u'AC905DD4AB2038E5F7EABEAE792AC41B', u'PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)', u'euc_jp', u'c:\\test\\TXT', u'normal.txt'), 
(u'password', u'pwd_password', u'(?i)password', u'euc_jp', u'c:\\test\\TXT', u'normal.txt'), 
(u'passw', u'pwd_passw', u'(?i)passw', u'euc_jp', u'c:\\test\\TXT', u'normal.txt'), 
(u'900e3f2dd4efc9892793222d7a1cee4a', u'PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)', u'cp932', u'c:\\test\\TXT', u'normal.txt'), 
(u'AC905DD4AB2038E5F7EABEAE792AC41B', u'PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)', u'cp932', u'c:\\test\\TXT', u'normal.txt'), 
(u'password', u'pwd_password', u'(?i)password', u'cp932', u'c:\\test\\TXT', u'normal.txt'), 
(u'passw', u'pwd_passw', u'(?i)passw', u'cp932', u'c:\\test\\TXT', u'normal.txt'), 
(u'900e3f2dd4efc9892793222d7a1cee4a', u'PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)', u'euc_jisx0213', u'c:\\test\\TXT', u'normal.txt'), 
(u'AC905DD4AB2038E5F7EABEAE792AC41B', u'PWD_MD5', u'(\\b[A-Fa-f0-9]{32}\\b)', u'euc_jisx0213', u'c:\\test\\TXT', u'normal.txt'), 
(u'password', u'pwd_password', u'(?i)password', u'euc_jisx0213', u'c:\\test\\TXT', u'normal.txt'), 
(u'passw', u'pwd_passw', u'(?i)passw', u'euc_jisx0213', u'c:\\test\\TXT', u'normal.txt')
)

#PDF:
PDF_data_brief=(((u'Applicat', 'applicat', u'(?i)applicat'), 
  (u'Applicat', 'applicat', u'(?i)applicat'), 
  (u'Applicat', 'applicat', u'(?i)applicat'), 
  (u'applicat', 'applicat',u'(?i)applicat'), 
  (u'Applicat', 'applicat', u'(?i)applicat'), 
  (u'Applicat', 'applicat', u'(?i)applicat'), 
  (u'Applicat', 'applicat', u'(?i)applicat'), 
  (u'applicat', 'applicat', u'(?i)applicat'), 
  (u'applicat', 'applicat', u'(?i)applicat'), 
  (u'applicat', 'applicat', u'(?i)applicat'), 2), 
  
 ((u'Applicat', 'applicat', u'(?i)applicat'), 
  (u'applicat', 'applicat', u'(?i)applicat'), 
  (u'Applicat', 'applicat', u'(?i)applicat'), 
  (u'applicat', 'applicat', u'(?i)applicat'), 
  (u'Applicat', 'applicat', u'(?i)applicat'), 
  (u'Applicat', 'applicat', u'(?i)applicat'), 3),
  
('c:\\test\\PDF', 'ztest.pdf'))

PDF_data_tuple=(
(u'Applicat', 'applicat', u'(?i)applicat', u'2', 'c:\\test\\PDF','ztest.pdf'), 
(u'Applicat', 'applicat', u'(?i)applicat', u'2', 'c:\\test\\PDF', 'ztest.pdf'), 
(u'Applicat', 'applicat', u'(?i)applicat', u'2', 'c:\\test\\PDF', 'ztest.pdf'), 
(u'applicat', 'applicat', u'(?i)applicat', u'2', 'c:\\test\\PDF', 'ztest.pdf'), 
(u'Applicat', 'applicat', u'(?i)applicat', u'2', 'c:\\test\\PDF', 'ztest.pdf'), 
(u'Applicat','applicat', u'(?i)applicat', u'2', 'c:\\test\\PDF', 'ztest.pdf'), 
(u'Applicat', 'applicat', u'(?i)applicat', u'2', 'c:\\test\\PDF', 'ztest.pdf'), 
(u'applicat', 'applicat', u'(?i)applicat', u'2', 'c:\\test\\PDF', 'ztest.pdf'), 
(u'applicat', 'applicat', u'(?i)applicat', u'2', 'c:\\test\\PDF', 'ztest.pdf'), 
(u'applicat', 'applicat', u'(?i)applicat', u'2', 'c:\\test\\PDF', 'ztest.pdf'), 
(u'Applicat', 'applicat', u'(?i)applicat', u'3', 'c:\\test\\PDF', 'ztest.pdf'), 
(u'applicat', 'applicat', u'(?i)applicat', u'3', 'c:\\test\\PDF', 'ztest.pdf'), 
(u'Applicat', 'applicat', u'(?i)applicat', u'3', 'c:\\test\\PDF', 'ztest.pdf'), 
(u'applicat', 'applicat', u'(?i)applicat', u'3', 'c:\\test\\PDF', 'ztest.pdf'), 
(u'Applicat', 'applicat', u'(?i)applicat', u'3', 'c:\\test\\PDF', 'ztest.pdf'), 
(u'Applicat', 'applicat', u'(?i)applicat', u'3', 'c:\\test\\PDF', 'ztest.pdf')
)

XLS_data_brief=((('username', 'username_username', u'(?i)username', 1, 1), 
('password', 'pwd_password', u'(?i)password', 1, 2), u'Basic_sheet'), 

(('3400 0000 0000 009', 'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', 2, 1), 
('340000000000009', 'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', 3, 1), 
('3400-0000-0000-009', 'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', 4, 1), 
('378282246310005', 'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', 5, 1), 
('371449635398431', 'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}',6, 1), 
('378734493671000', 'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', 7, 1), 
('5610591081018250', 'CreditCard_16numbers', u'\\d{16}', 8, 1), 
('5019717010103742', 'CreditCard_16numbers', u'\\d{16}', 10, 1), 
('6011389863535507', 'CreditCard_16numbers', u'\\d{16}', 11, 1), 
('6011126236587298', 'CreditCard_16numbers', u'\\d{16}', 12, 1), 
('6011659209827515', 'CreditCard_16numbers', u'\\d{16}', 13, 1), 
('6011097109013169', 'CreditCard_16numbers', u'\\d{16}', 14, 1), 
('6011506937115277', 'CreditCard_16numbers', u'\\d{16}', 15, 1), 
('30569309025904', 'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', 16, 1), 
('38520000023237', 'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', 17, 1), 
('3000 0000 0000 04', 'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', 18, 1), 
('30000000000004', 'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', 19, 1), 
('3000-0000-0000-04', 'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', 20, 1), 
('6011111111111117', 'CreditCard_16numbers', u'\\d{16}', 21, 1), 
('6011000990139424', 'CreditCard_16numbers', u'\\d{16}', 22, 1), 
('3530111333300000', 'CreditCard_16numbers', u'\\d{16}', 23, 1), 
('3566002020360505', 'CreditCard_16numbers', u'\\d{16}', 24, 1), 
('5500 0000 0000 0004', 'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', 25, 1), 
('5500000000000004', 'CreditCard_16numbers', u'\\d{16}', 26, 1), 
('5500-0000-0000-0004', 'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', 27, 1), 
('5555555555554444', 'CreditCard_16numbers', u'\\d{16}', 28, 1), 
('5105105105105100', 'CreditCard_16numbers', u'\\d{16}', 29, 1), 
('6331101999990016', 'CreditCard_16numbers', u'\\d{16}', 30, 1), 
('4111 1111 1111 1111', 'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', 31, 1), 
('4111111111111111', 'CreditCard_16numbers', u'\\d{16}', 32, 1), 
('4111-1111-1111-1111', 'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', 33, 1), 
('4111111111111111', 'CreditCard_16numbers', u'\\d{16}', 34, 1), 
('4012888888881881', 'CreditCard_16numbers', u'\\d{16}', 35, 1), 
('4222222222222','CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', 36, 1), u'CreditCards'), 

('c:\\test\\XLS', 'test.xlsx'))

XLS_data_tuple=(
(u'username', u'username_username', u'(?i)username', u'1:1:Basic_sheet', u'c:\\test\\XLS', u'test.xlsx'), 
(u'password', u'pwd_password', u'(?i)password', u'1:2:Basic_sheet', u'c:\\test\\XLS', u'test.xlsx'), 
(u'3400 0000 0000 009', u'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', u'2:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'340000000000009', u'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', u'3:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'3400-0000-0000-009', u'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', u'4:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'378282246310005', u'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', u'5:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'371449635398431', u'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', u'6:1:CreditCards', u'c:\\test\\XLS',u'test.xlsx'), 
(u'378734493671000', u'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}',u'7:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'5610591081018250', u'CreditCard_16numbers', u'\\d{16}', u'8:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'5019717010103742', u'CreditCard_16numbers', u'\\d{16}', u'10:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'6011389863535507', u'CreditCard_16numbers', u'\\d{16}', u'11:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'6011126236587298', u'CreditCard_16numbers', u'\\d{16}', u'12:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'6011659209827515', u'CreditCard_16numbers', u'\\d{16}', u'13:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'6011097109013169', u'CreditCard_16numbers', u'\\d{16}', u'14:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'6011506937115277', u'CreditCard_16numbers', u'\\d{16}',u'15:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'30569309025904', u'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', u'16:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'38520000023237', u'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', u'17:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'3000 0000 0000 04', u'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', u'18:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'30000000000004', u'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', u'19:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'3000-0000-0000-04', u'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', u'20:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'6011111111111117', u'CreditCard_16numbers', u'\\d{16}', u'21:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'6011000990139424', u'CreditCard_16numbers', u'\\d{16}', u'22:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'3530111333300000', u'CreditCard_16numbers', u'\\d{16}', u'23:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'3566002020360505', u'CreditCard_16numbers', u'\\d{16}', u'24:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'5500 0000 0000 0004', u'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', u'25:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'5500000000000004', u'CreditCard_16numbers', u'\\d{16}', u'26:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'5500-0000-0000-0004', u'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', u'27:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'5555555555554444', u'CreditCard_16numbers', u'\\d{16}', u'28:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'5105105105105100', u'CreditCard_16numbers', u'\\d{16}', u'29:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'6331101999990016', u'CreditCard_16numbers', u'\\d{16}', u'30:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'4111 1111 1111 1111', u'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', u'31:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'4111111111111111', u'CreditCard_16numbers', u'\\d{16}', u'32:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'4111-1111-1111-1111', u'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', u'33:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'4111111111111111', u'CreditCard_16numbers', u'\\d{16}', u'34:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'4012888888881881', u'CreditCard_16numbers', u'\\d{16}', u'35:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx'), 
(u'4222222222222', u'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', u'36:1:CreditCards', u'c:\\test\\XLS', u'test.xlsx')
)

DOC_data_tuple=(
(u'Password', 'pwd_password', u'(?i)password', u'2', 'c:\\test\\DOC', 'xtest.doc'), 
(u'Passw', 'pwd_passw', u'(?i)passw', u'2', 'c:\\test\\DOC', 'xtest.doc'), 
(u'1111-2222-3333-4444', 'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', u'4', 'c:\\test\\DOC', 'xtest.doc')
)

DOCX_data_tuple=(
(u'Password', u'pwd_password', u'(?i)password', u'2', u'c:\\test\\DOC_reader', u'xtest.docx'), 
(u'Passw', u'pwd_passw', u'(?i)passw', u'2', u'c:\\test\\DOC_reader', u'xtest.docx'), 
(u'1111-2222-3333-4444', u'CreditCard_ALL', u'(?:\\d[ -]*?){13,16}', u'4', u'c:\\test\\DOC_reader', u'xtest.docx')
)

#myAnalysisdata=DOCX_data_tuple
#myAnalysistype='docx'
#myAnalysisconn,myAnalysisc=create_analysis_and_fill_with_data(myAnalysisdata,myAnalysistype, print_out=False)

#PRINT DATABASE CONTENTS
#total_rows(myAnalysisc, Analysis_table_name, print_out=True)
#table_col_info(myAnalysisc, Analysis_table_name, print_out=True)
#values_in_col(myAnalysisc, Analysis_table_name, print_out=True) # slow on large data bases
#myAnalysisdata=values_all_tuple(myAnalysisc, Analysis_table_name, print_out=False)

#tuple2csv(myAnalysisdata)

#db_commit(myAnalysisconn)
#db_close(myAnalysisconn)

