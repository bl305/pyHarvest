#!/usr/bin/env python
# coding=utf-8

import re

mydata='''This is a simple text that could be matched 4444 4444 4444 4444 
aaa:password 
bbb Password'''

mypatterns=(
##search simple string, ignore case:
##search_string(r'(?i)password',sheet)

#CREDIT CARD DATA
('CreditCard_16numbers',ur'\d{16}'),
('CreditCard_ALL',ur'(?:\d[ -]*?){13,16}'),
('CreditCard_VISA',ur'^4\d{3}([\ \-]?)\d{4}\1\d{4}\1\d{4}'),
('CreditCard_MASTER',ur'^5[1-5]\d{2}([\ \-]?)\d{4}\1\d{4}\1\d{4}'),
('CreditCard_DISCOVER',ur'^6(?:011|22(?:1(?=[\ \-]?(?:2[6-9]|[3-9]))|[2-8]|9(?=[\ \-]?(?:[01]|2[0-5])))|4[4-9]\d|5\d\d)([\ \-]?)\d{4}\1\d{4}\1\d{4}'),
('CreditCard_JAPAN',ur'^35(?:2[89]|[3-8]\d)([\ \-]?)\d{4}\1\d{4}\1\d{4}'),
('CreditCard_AMEX',ur'(?<!\-|\.)3[47]\d\d([\ \-]?)(?<!\d\ \d{4}\ )(?!(\d)\2{5}|123456|234567|345678)\d{6}(?!\ \d{5}\ \d)\1(?!(\d)\3{4}|12345|56789)\d{5}(?!\-)(?!\.\d)'),
('CreditCard_AMEX_notdash',ur'^3[47]\d\d([\ \-]?)\d{6}\1\d{5}'),
('CreditCard_CHINA_UNION',ur'^62[0-5]\d{13,16}'),
('CreditCard_MAESTRO',ur'^(?:5[0678]\d\d|6304|6390|67\d\d)\d{8,15}'),
('CreditCard_VISA_MASTER_AMEX_DISCOVER',ur'(?:3[47]\d{2}([\ \-]?)\d{6}\1\d|(?:(?:4\d|5[1-5]|65)\d{2}|6011)([\ \-]?)\d{4}\2\d{4}\2)\d{4}'),

#MD5
('PWD_MD5',ur'(\b[A-Fa-f0-9]{32}\b)'),

#SHA1 NOT WORKING
('PWD_SHA1',ur'\b([a-f0-9]{40})\b'),

#simple strings ignore case password
#('pwd_password',r'(?i)password'),
#PASSWORD STRING case insensitive
('pwd_password',ur'(?i)password'),
#('pwd_spanish',ur'(?i)'),
('pwd_pwd',ur'(?i)pwd'),
('pwd_passw',ur'(?i)passw'),
#USERNAME STRING case insensitive
('username_username',ur'(?i)username'),
('username_spanish',ur'(?i)usuario'),

)

def find_pattern (data,patterns=mypatterns,aggressive=0):
	matches=()
	for i in range(len(patterns)):

		if aggressive==1:
			#print "[+] Starting aggressive search"
			creditcard=re.search(ur'^creditcard',patterns[i][0].lower())
			try:
				if creditcard:
					#print "[+] Cleaning data for credit card checks",data
					workdata1=data.replace(" ","")
					workdata2=workdata1.replace("-","")
					workdata3=workdata2.replace(",","")
					workdata4=workdata3.replace(".","")
					tmpdata=workdata4
				regex = re.compile(patterns[i][1])
				it = re.finditer(regex, tmpdata)
				#print "[+] Searching for pattern:\n%s in \n%s"%(patterns[i][1],data)
				try:
					if it:
						for mymatch in it:
							#print "[+] Aggressive search:",data
							#print "[+] Match found!! String:%s Pattern:%s SearchValue:%s"%(mymatch.group(),patterns[i][0],patterns[i][1])
							matches+=(mymatch.group(),patterns[i][0],patterns[i][1]),
				except Exception,e:
					print e
					pass
				
			except:
				pass
		else:

			regex = re.compile(patterns[i][1])
			it = re.finditer(regex, data)
			#print "[+] Searching for pattern:\n%s in \n%s"%(patterns[i][1],data)
			try:
				if it:
					for mymatch in it:
						#print "[+] Normal search:",data
						#print "[+] Match found!! String:%s Pattern:%s SearchValue:%s"%(mymatch.group(),patterns[i][0],patterns[i][1])
						matches+=(mymatch.group(),patterns[i][0],patterns[i][1]),
			except Exception,e:
				print e
				pass
	return matches
	
#matchtuple=find_pattern(mydata,mypatterns,0)
#print matchtuple

