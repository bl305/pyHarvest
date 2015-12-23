from packages import *

#Gather SMB data from the list specified.
#file format:
#smb;remotehostname;remote IP;share;domain;fileshare;username;password;

#########################################################
##############SMB PARAMETERS START#######################
#########################################################
#SMBusername='user1'
SMBusername='blendvay'
SMBusername=convert_to_unicode(SMBusername)
#SMBpassword='Asdf1234'
SMBpassword = raw_input('password:')
SMBpassword=convert_to_unicode(SMBpassword)
#SMBremotesystem = 'FileServer'
SMBremotesystem = 'GUS-CFD-80-2061'
SMBremotesystem=convert_to_unicode(SMBremotesystem)
#SMBremoteip = '192.168.178.52'
SMBremoteip = '127.0.0.1'
SMBremoteip=convert_to_unicode(SMBremoteip)
#SMBlocalsystem='GUS-CFD-80-2061'
SMBlocalsystem = socket.gethostname()
SMBlocalsystem=convert_to_unicode(SMBlocalsystem)
#SMBdomain='WORKGROUP'
SMBdomain='CORPLEAR'
SMBmydomain=convert_to_unicode(SMBdomain)
#SMBfileshare='FileShare'
SMBfileshare='TestShare'
SMBfileshare=convert_to_unicode(SMBfileshare)
SMBoutdir="./DataGathered/SMB/"
SMBoutdir=convert_to_unicode(SMBoutdir)
SMBtop="/"
SMBtop=convert_to_unicode(SMBtop)
SMBtop=os.path.normpath(SMBtop).replace('//','/')
#if you want to find all shares and use them set this to 1, else the myfileshare will be used
SMBgetshares=0

#create empty directories?
SMBcreateemptydirs=0

#download files?
SMBdownloadfiles=1

#set verbosity
#-1 - no messages
#0 - tuple of results
#1 - summary information
#2 - basic information, positive info
#3 - detailed information, positive, negative
#4 - go crazy about it...
SMBverbosity=2
#########################################################
##############SMB PARAMETERS END#########################
#########################################################

#########################################################
##############FTP PARAMETERS START#######################
#########################################################
#domain name or server ip:
#ftp = FTP('ftp.fau.de')
FTPserver='ftp.au.debian.org'
FTPdir='/pub/linux/debian/doc/'
#FTPdir='/pub/linux/debian/'

#myftpserver='192.168.178.182'
#myftpdir='/'
FTPusername="anonymous"
FTPpassword="anony@mo.us"

#limit to pull files smaller than this
#http://www.whatsabyte.com/P1/byteconverter.htm
FTPflimit_1K=1024
FTPflimit_1M=1048576
FTPflimit_1GB=1073741824
#flimit_max:9223372036854775807
FTPflimit=FTPflimit_1K*1
#output directpry path
#current dir:
#outdir=os.path.realpath('.')
FTPoutdir="./DataGathered/FTP"

FTPskiplist=('/dev','/bin','/opt','initrd.img','vmlinuz')

FTPdownloadfiles=1
FTPcreateemptydirs=0

#set verbosity
#-1 - no messages
#0 - tuple of results
#1 - summary information
#2 - basic information, positive info
#3 - detailed information, positive, negative
#4 - go crazy about it...
FTPverbosity=1

#########################################################
##############FTP PARAMETERS END$$#######################
#########################################################



#Collect SMB data
SMBallitems=smb_main(SMBusername,SMBpassword,SMBlocalsystem,SMBremotesystem,SMBremoteip,SMBdomain,SMBfileshare,SMBtop,SMBoutdir,SMBdownloadfiles,SMBcreateemptydirs,SMBgetshares,averbosity=SMBverbosity)
#print "\n"
#print SMBallitems


#Collect FTP data
FTPallitems=ftp_main(FTPserver,FTPdir,FTPusername,FTPpassword,FTPflimit,FTPoutdir,FTPskiplist,FTPdownloadfiles,FTPcreateemptydirs,averbosity=FTPverbosity)
#print "\n"
#print FTPallitems

#Create and open database:
Filesconn, Filesc = db_connect(Files_sqlite_file)
create_host_db(Filesconn, Files_create_script,print_out=False)

#Save SMB data to database
#insert_db_file_data(Filesc,Files_table_name,SMBallitems,False)
#db_commit(Filesconn)

#Save FTP data to database
insert_db_file_data(Filesc,Files_table_name,FTPallitems,False)
db_commit(Filesconn)

#Commit and close database
db_commit(Filesconn)
db_close(Filesconn)
