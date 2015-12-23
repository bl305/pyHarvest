#!/usr/bin/env python
# coding=utf-8

#http://blog.digitally-disturbed.co.uk/2012/04/ive-started-work-on-pulling-text-from.html
#http://blog.digitally-disturbed.co.uk/2012/04/reading-microsoft-word-doc-files-in.html

import sys
import os
import re
import struct
from pyHarvest_xmod_patternmatch import *
from pyHarvest_xmod_OleDocument import OleDocument, ReaderError

DOCNONASCIIPATTERN8 = re.compile(r"[\x7F-\xFF]")
DOCNONASCIIPATTERN16 = re.compile(ur"[\u007F-\uFFFF]")
DOCTABLECLEAN = re.compile(r"[\x01-\x08]")
DOCSTRIPPATTERN = re.compile(r"\r")
DOCHYPERLINKPATTERN = re.compile(
    r"\x13.*HYPERLINK.*\"(?P<uri>.*)\".*\x14(?P<display>.*)\x15")



class DOCReader(object):
    
    def __init__(self, file_name):
        self.file_name = file_name
        self.document = OleDocument(file_name)
        self.non_ascii_pattern8 = DOCNONASCIIPATTERN8
        self.non_ascii_pattern16 = DOCNONASCIIPATTERN16
        self.table_cleanup = DOCTABLECLEAN
        self.strip_pattern = DOCSTRIPPATTERN
        self.hyperlink_pattern = DOCHYPERLINKPATTERN
        self.file_version = "Unknown Version"
                
    def extract_text(self):
        #First we need to pull out the WordDocument stream
        #THis has most of the data we need
        doc_stream = self.document.read_stream("WordDocument")
        #The magic and version words define what version document this is
        #We dont handle pre-word 6 documents
        magic, version, flags = struct.unpack("<HH6xH", doc_stream[:12])
        if magic != 0xA5EC and magic != 0xA5DC:
            raise ReaderError("Invalid format - not a Word doc file")
        if version < 101:
            raise ReaderError("Very old doc file - cant handle before Word 95")
        elif version == 101 or version in range(103, 105):
            self.file_version = "Word 95"
            buff = self._process_word95(doc_stream)
        elif version >= 193:
            self.file_version = "Word 97 - 2003"
            buff = self._process_word97(doc_stream, flags)
        else:
            raise ReaderError("Unknown version of Word")
        return buff
    
    def _clean_hyperlinks(self, buff):
        #Word marks up hyperlinks with a certain markup.
        #We want to strip this out, pull out the hyperlink text and uri,
        # then add this to the text
        for match in self.hyperlink_pattern.finditer(buff):
            uri, display = match.groups()
            buff = self.hyperlink_pattern.sub("%s (link: %s)" % (display, uri),
                                              buff, 1)
        return buff
    
    def _process_word95(self, doc_stream):
        #This version is so much easier to handle!
        #The text start offset and end offset are early on in the stream.
        #Pull them out, try clean up the text (seems to be ascii) and thats it
        text_start, text_end = struct.unpack_from("<II", doc_stream, 0x18)
        buff = doc_stream[text_start:text_end]
        buff = self.non_ascii_pattern8.sub("", buff)
        buff = self.table_cleanup.sub(" ", unicode(buff , "utf8"))
        buff = self._clean_hyperlinks(buff)
        return self.strip_pattern.sub("\r\n", buff)
        
    def _process_word97(self, doc_stream, flags):
        #This is where it gets ugly!
        #Depending on the flags, you need to pull out another stream
        #Its almost always '1Table'
        if flags & 0x40:
            table_stream_name = "1Table"
        else:
            table_stream_name = "0Table"
        #Now, from the WordDocument stream pull out the size of the text
        #If there's any text in headers etc... then we need to add the extra
        # amount of text along with 1 extra char (Dont know why the extra 1!!!)
        offset = 62
        count = struct.unpack_from("<H", doc_stream, offset)[0]
        offset += 2
        text_size, foot_size, header_size, macro_size, annotation_size, \
            endnote_size, textbox_size, headertextbox_size = \
            struct.unpack_from("12x8I", doc_stream, offset)
        #If any sizes other than text size are non zero, add them up and add 1
        if foot_size or header_size or macro_size or annotation_size or \
                endnote_size or textbox_size or headertextbox_size:
            final_cp = text_size + foot_size + header_size + macro_size + \
                annotation_size + endnote_size + textbox_size + \
                headertextbox_size + 1
        else:
            final_cp = text_size
        #Skip across some unused structures to get an offset to the table stream
        offset += (count * 4) 
        offset += (66 * 4) + 2 #Add offset from main block + count variable
        clx_offset, clx_size = struct.unpack_from("<II", doc_stream, offset)
        table_stream = self.document.read_stream(table_stream_name)
        magic, size = struct.unpack_from("<BH", table_stream, clx_offset)
        if magic != 0x02:
            raise ReaderError("Not a valid clxt in the table stream")
        #Now read a list of cp offsets showing how the text is broken up
        cp_list = []
        offset = clx_offset + 5
        for i in range(size / 4):
            cp = struct.unpack_from("<I", table_stream, offset)[0]
            cp_list.append(cp)
            offset += 4
            if cp == final_cp:
                break
        if i == (size / 4) - 1:
            raise ReaderError("Parse error - doc file has no final cp")
        #For each cp offset we need to see if the text is 8 or 16 bit, get a
        # stream offset and process the text chunk
        buff = u""
        for i in range(len(cp_list[:-1])):
            fc = struct.unpack_from("<2xI", table_stream, offset)[0]
            stream_offset = fc & (0xFFFFFFFF >> 2)
            compressed = fc & (0x01 << 30)
            next_cp = cp_list[i + 1]
            cp = cp_list[i]
            buff += self._process_block97(stream_offset, cp, next_cp, compressed,
                                            doc_stream)
            offset += 8
        return self.strip_pattern.sub("\r\n", buff)
            
    def _process_block97(self, text_offset, cp, next_cp, compressed,
                         doc_stream):
        #For each text block we need to read the data and try clean it up.
        #The data has special markup for tables and hyperlinks as well as other
        # stuff that can be quite nasty of you dont clean it up
        if compressed:
            text_offset /= 2
            last = (text_offset) + next_cp - cp - 1
            buff = self.non_ascii_pattern8.sub("", doc_stream[text_offset:last])
            buff = self.table_cleanup.sub(" ", unicode(buff , "utf8"))
            return self._clean_hyperlinks(buff)
        else:
            last = text_offset + 2 * (next_cp - cp)
            buff = doc_stream[text_offset:last]
            buff = unicode(buff , "utf16", errors="replace")
            buff = self._clean_hyperlinks(buff)
            buff = self.non_ascii_pattern16.sub("", buff)
            return self.table_cleanup.sub(" ", buff)            

def doc_full_search_tuple(apath,verbosity=0):
	mytext=DOCReader(apath).extract_text()
	mytext=tuple(mytext.split('\r\n'))
	mypath=os.path.dirname(apath)
	myfilename=os.path.basename(apath)
	matches=()
	for c1 in range(len(mytext)):
		mymatch=find_pattern(mytext[c1])
		if mymatch:
			for i1 in range(len(mymatch)):
				if verbosity>1:
					print "[+] MATCH for pattern \"%s\" on page #%d !!!"%(mymatch[i1],i1)
				matches+=(mymatch[i1][0],mymatch[i1][1],mymatch[i1][2],unicode(c1),mypath,myfilename),
	return matches

def doc_full_search_list(apath,averbosity=0):
	myinput=doc_full_search_tuple(apath,verbosity=averbosity)
	result=""
	for i1 in range(len(myinput)):
		result+="%s\t%s\t%s\t%s\t%s\t%s\n"%(unicode(myinput[i1][0]),unicode(myinput[i1][1]),unicode(myinput[i1][2]),unicode(myinput[i1][3]),unicode(myinput[i1][4]),unicode(myinput[i1][5]))
	return result

if __name__ == '__main__':
	#mypath='c:\\test\\xtest.doc'
	#print doc_full_search_tuple(mypath)
	pass
