# coding=utf-8
from packages import *
import os

#SET PARAMETERS
myverbosity=-1
mymaxencode=5

TXT_filetypes=(
#simple text files
'txt','lst',
#config files
'ini','cfg',
#programming languages
'c','cpp',
#scripts
'vbs','py','pl')

XLS_filetypes=('xls','xlsx')
DOC_filetypes=('doc',)
DOCX_filetypes=('docx',)
PDF_filetypes=('pdf',)


#TEMPLATE FILES
myXLSpath=r'c:\LENBAL\Trainings\Securitytube_Python_Expert_PRIVATE\My_Network_Discovery_Project\Main_Program\AllTestFiles\XLS\test.xlsx'
myTXTpath=r'c:\LENBAL\Trainings\Securitytube_Python_Expert_PRIVATE\My_Network_Discovery_Project\Main_Program\AllTestFiles\TXT\normal.txt'
#myTXTpath=r'c:\LENBAL\Trainings\Securitytube_Python_Expert_PRIVATE\My_Network_Discovery_Project\Main_Program\AllTestFiles\TXT\unicode.txt'
#myTXTpath=r'c:\LENBAL\Trainings\Securitytube_Python_Expert_PRIVATE\My_Network_Discovery_Project\Main_Program\AllTestFiles\TXT\unicode_big.txt'
#myTXTpath=r'c:\LENBAL\Trainings\Securitytube_Python_Expert_PRIVATE\My_Network_Discovery_Project\Main_Program\AllTestFiles\TXT\unicode_utf8.txt'
#myTXTpath=r'c:\LENBAL\Trainings\Securitytube_Python_Expert_PRIVATE\My_Network_Discovery_Project\Main_Program\AllTestFiles\TXT\x.txt'
#myPDFpath=r'c:\LENBAL\Trainings\Securitytube_Python_Expert_PRIVATE\My_Network_Discovery_Project\Main_Program\AllTestFiles\PDF\test.pdf'
#myPDFpath=r'c:\LENBAL\Trainings\Securitytube_Python_Expert_PRIVATE\My_Network_Discovery_Project\Main_Program\AllTestFiles\PDF\xtest.pdf'
myPDFpath=r'c:\LENBAL\Trainings\Securitytube_Python_Expert_PRIVATE\My_Network_Discovery_Project\Main_Program\AllTestFiles\PDF\ztest.pdf'
myDOCpath=r'c:\LENBAL\Trainings\Securitytube_Python_Expert_PRIVATE\My_Network_Discovery_Project\Main_Program\AllTestFiles\DOC\xtest.doc'
myDOCXpath=r'c:\LENBAL\Trainings\Securitytube_Python_Expert_PRIVATE\My_Network_Discovery_Project\Main_Program\AllTestFiles\DOC\xtest.docx'
mydirpath=r'c:\LENBAL\Trainings\Securitytube_Python_Expert_PRIVATE\My_Network_Discovery_Project\Main_Program\AllTestFiles'
#mydirpath=r'c:\LENBAL\Trainings\Securitytube_Python_Expert_PRIVATE\My_Network_Discovery_Project\Main_Program\DataGathered'
#mypath=myTXTpath
#mypath=myXLSpath
#mypath=myPDFpath
#mypath=myDOCpath
#mypath=myDOCXpath

#PROGRAM START
def process_myfile(thepath,verbosity=0):
	#Select file type
	fileextension=""
	result=()
	if '.' in thepath:
		fileextension = thepath.rsplit('.', 1)[1]
	if fileextension in DOC_filetypes:
		doc_match=doc_full_search_tuple(thepath,myverbosity)
		if doc_match:
			result+=(doc_match,'doc')
			if verbosity>1:
				print doc_match
	elif fileextension in DOCX_filetypes:
		docx_match=docx_full_search_tuple(thepath,myverbosity)
		if docx_match:
			result+=(docx_match,'docx')
			if verbosity>1:
				print docx_match
	elif fileextension in XLS_filetypes:
		#PROCESS XLS
		#xls_match=xls_full_search_tuple(thepath,verbosity=myverbosity)
		xls_match=xls_full_search_tuple(thepath,myverbosity)
		if xls_match:
			result+=(xls_match,'xlsx')
			if verbosity>1:
				print xls_match
			#print xls_match[-1]
	elif fileextension in PDF_filetypes:
		pdf_match=pdf_full_search_tuple(thepath,myverbosity)
		if pdf_match:
			result+=(pdf_match,'pdf')
			if verbosity>1:
				print pdf_match
			#print pdf_match[-1]
	elif fileextension in TXT_filetypes:
		#PROCESS TXT
		#txt_match=txt_full_search_tuple(thepath,maxencode=mymaxencode,verbosity=myverbosity)
		txt_match=txt_full_search_tuple(thepath,mymaxencode,myverbosity)
		if txt_match:
			result+=(txt_match,'txt')
			if verbosity>1:
				print txt_match
			#print txt_match[-1]		
	else:
		print "[-] UNKNOWN filetype",thepath
	return result

def process_localdir(localdir,recursive=0):
	results=()
	if recursive==0:
		#files = [ f for f in os.listdir(localdir) if os.path.isfile(os.path.join(localdir,f)) ]
		for files in os.listdir(localdir):
			if os.path.isfile(os.path.join(localdir,files)):
				abspath=os.path.join(localdir,files)
				abspath = os.path.normpath(abspath).replace('//','/')
				#print abspath
				results+=(abspath,)
	else:
		for subdir, dirs, files in os.walk(localdir):
			for file in files:
				abspath=os.path.join(subdir,file)
				abspath = os.path.normpath(abspath).replace('//','/')
				#print abspath
				results+=(abspath,)
	return results

#print "##########################Main Program Started##########################"		
#ANALYSE A SPECIFIC FILE
#process_myfile(mypath)

#ANALYSE ALL FILES IN A SPECIFIED DIRECTORY
filesindir=process_localdir(mydirpath,1)
Analysisconn, Analysisc = db_connect(Analysis_sqlite_file)
create_host_db(Analysisconn, Analysis_create_script,print_out=False)
filecount=len(filesindir)
filecounter=1
if filecount==0:
	print "No files to analyse"
for fn in range(len(filesindir)):
	mytext=process_myfile(filesindir[fn])
	print "Analysing file %d/%d %s"%(filecounter,filecount,filesindir[fn])
	filecounter+=1
	if mytext:
		ftype=mytext[1]
		mytextdata=mytext[0]
		insert_analysis_data(Analysisc,Analysis_table_name,mytextdata,ftype,print_out=False)
		db_commit(Analysisconn)
		pass

db_commit(Analysisconn)
db_close(Analysisconn)

print (raw_input('Press Enter to Exit!'))