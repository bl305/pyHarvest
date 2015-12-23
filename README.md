# pyHarvest
This is part of my project "giving back to the community" - free to use.
Python tool for harvesting interesting information from files, including limited discovery of files
You can find my project also on my website: http://itfanatic.com

Where sourcecode of someone else has been used, it is always referenced in my sourcecode. As much as possible. 
If someting is missing, please sugest me ASAP.

I decided to create a project for finding and analysing documents (regex match for credit card, social security number, password hashes, custom strings etc.) in the network using Python. It is useful in network audits, penetration tests and other kinds of assessments. Also, it is helpful if you're just looking for a quick solution for any of the topics covered below.

More to be followed...

I am not a programmer in any ways, so the scripts below are pretty ugly, but it serves the purpose they meant to do for me. Please feel free to use or modify them as needed. Any feedback also appreciated (info@ domain of this website). 

GitHub resource containing source code:

https://github.com/bl305/pyHarvest

It is modular primarily os-independent consisting of the following modules:
-pyHarvest DOC
-pyHarvest DOCX
-pyHarvest FTP
-pyHarvest PDF
-pyHarvest PatternMatch
-pyHarvest SMB
-pyHarvest SQLITE
-pyHarvest TXT and other text formats
-pyHarvest XLS and XLSX

Tasks planned next:
SMB module implement size, name and depth limits
patternmatch module add more patterns
ERROR/Exception handling in many-many cases...I didn't pay much attention to this
Integrate the discovery module with Analysis module (not sure about this yet)
DB module, match Files database to Analysis database