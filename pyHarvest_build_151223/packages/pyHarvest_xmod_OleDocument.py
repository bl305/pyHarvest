#!/usr/bin/env python
# coding=utf-8
#http://blog.digitally-disturbed.co.uk/2012/04/ive-started-work-on-pulling-text-from.html
#http://blog.digitally-disturbed.co.uk/2012/04/reading-microsoft-word-doc-files-in.html

import os
import sys
import struct
import re
from collections import namedtuple

WPSSTRIPPATTERN = re.compile(r"\r")

class ReaderError(Exception): pass

class OleDocument(object):
    
    def __init__(self, file_name):
        self.file_name = file_name
        self.sectors = []
        self.directories = {}
        self._parse_contents()
        
    def _read_fat_sector(self, fat_sector, fd):
        fd.seek(self.sector_size*(fat_sector+1), os.SEEK_SET)
        for i in range(self.sector_size / 4):
            sector = struct.unpack("<I", fd.read(4))[0]
            yield sector                
        
    def _parse_contents(self):
        with open(self.file_name, "rb") as fd:
            sig = fd.read(8)
            if sig != "\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1":
                raise ReaderError("Not a valid Ole Storage Document")
            header = fd.read(68)
            sector_shift, mini_sector_shift, fat_sector_count, \
                first_dir_sector, first_mini_sector, mini_sector_count,  \
                = struct.unpack("<22xHH10xII8xII8x", header)
            self.sector_size = 1 << sector_shift
            self.mini_sector_size = 1 << mini_sector_shift
            fat_sectors = []
            
            for i in range(fat_sector_count):
                fat_sectors.append(struct.unpack("<I", fd.read(4))[0])
            for fat_sector in fat_sectors:
                for sector in self._read_fat_sector(fat_sector, fd):
                    self.sectors.append(sector)
                
            #Now read the directories
            buff = ''
            for count, dir_sector in \
                    enumerate(self._get_sectors(first_dir_sector)):
                fd.seek(self.sector_size*dir_sector+self.sector_size,
                        os.SEEK_SET)
                buff += fd.read(self.sector_size)
            for i in range((count+1)*4):
                name, sector, size = struct.unpack("<64s52xII4x",
                                                   buff[i*128:(i+1)*128])
                name = re.sub("\x00", "", unicode(name, "UTF16"))
                self.directories[name] = (sector, size)
                
    def _get_sectors(self, sector):
        while True:
            if sector == 0xFFFFFFFE: #Last directory
                break
            yield sector
            sector = self.sectors[sector] 
                        
                                
    def read_stream(self, name):
        name = unicode(name)
        if name not in self.directories:
            raise ReaderError("No stream called %s" % name)
        start, size = self.directories[name]
        buff = ""
        with open(self.file_name, "rb") as fd:
            for sector in self._get_sectors(start):
                fd.seek(self.sector_size*sector+self.sector_size, os.SEEK_SET)
                buff += fd.read(self.sector_size)
                size -= self.sector_size
                if size <= 0:
                    break
        return buff

class WPSReader(object):
    
    def __init__(self, file_name):
        self.document = OleDocument(file_name)
        self.strip_pattern = WPSSTRIPPATTERN

    def _process_entries(self, entry_buff):
        magic, local, next_offset = struct.unpack("<HHI", entry_buff[:8])
        if magic != 0x01F8:
            raise ReaderError("Invalid format - Entry magic tag incorrect")
        entry_pos = 0x08 #2 WORDS & 1 DWORD
        for i in range(local):
            size = struct.unpack("<H", entry_buff[entry_pos:entry_pos+0x2])[0]
            name, offset, entry_size = struct.unpack("<2x4s10xII",
                                        entry_buff[entry_pos:entry_pos+size])
            if name == "TEXT": #Success!
                return (local, 0x00, offset, entry_size)
            entry_pos += size
        return (local, next_offset, 0x00, 0x00) #Needs to be run again
        
    def extract_text(self):
        buff = self.document.read_stream("CONTENTS")
        total_entries = struct.unpack("<12xH",  buff[:14])[0]
        entries_pos = 24
        while True:
            entries, next_offset, text_header_offset, text_size = \
                self._process_entries(buff[entries_pos:])           
            if text_size: #TEXT found
                break
            total_entries -= entries
            if total_entries and next_offset:
                entries_pos = next_offset #Move to next block
            else:
                raise ReaderError("Unable to find TEXT secion. File corrupt?")
        text = buff[text_header_offset:text_header_offset+text_size]
        return self.strip_pattern.sub("\r\n", unicode(text, "UTF16"))
        
        
if __name__ == '__main__':
    reader = WPSReader(sys.argv[1])
    print reader.extract_text()