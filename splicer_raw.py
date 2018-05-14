# raw voltage splicer
# 1st argument is path to directory containing all raw extracted files
# 2nd argument is divider
# 3rd argument is output file name
# example :  python raw_splicer.py "/datax2/greg_raw_splicer/RAWFILE2/" 2 "test.raw"

import os
import glob
import sys
import math
import numpy

os.chdir(sys.argv[1])
list_files = os.listdir(sys.argv[1])	# list all files from the data set
numfiles = len(list_files)				# counts number of files in dataset

if numfiles == 0:
	print("error : no file corresponding to the dataset indicated")
	sys.exit()
else:
	print "there are " + str(numfiles) + " files in the data set"

idx = -1
cenfreq = [0]*numfiles	# array of central frequencies to order files
obsbw = [0]*numfiles	# array of bandwidths
NumBlocs = [0]*numfiles	# array of number of blocks per raw file

for fname in list_files:
	idx = idx + 1
	fread = open(fname,'rb')	# open first file of data set
	currline = str(fread.read(80))		# reads first line
	nHeaderLines = 1
	while currline[0:3] != 'END':		# until reaching end of header
		currline = str(fread.read(80))	# read new header line
		if currline[0:9] == 'OBSFREQ =':	# read cenral frequency
			cenfreq[idx] = float(currline[9:])
		if currline[0:9] == 'OBSBW   =':	# read bandwidth
			obsbw[idx] = float(currline[9:])
		if currline[0:9] == 'OBSNCHAN=':	# read number of coarse channels
			obsnchan = float(currline[9:])
		if currline[0:9] == 'NBITS   =':	# read quantization
			nbits = float(currline[9:])
		if currline[0:9] == 'DIRECTIO=':	# read directio flag
			ndirectio = float(currline[9:])
		if currline[0:9] == 'BLOCSIZE=':	# read block size
			nblocsize = float(currline[9:])
		if currline[0:9] == 'PKTSIZE =':	# read packet size
			nPktSize = float(currline[9:])
		nHeaderLines = nHeaderLines + 1		# counts number of lines in header
	fread.close()
	nPadd = 0
	if ndirectio == 1:
		nPadd = int((math.floor(80.*nHeaderLines/512.)+1)*512 - 80*nHeaderLines)
	statinfo = os.stat(fname)
	NumBlocs[idx] = int(round(statinfo.st_size / (nblocsize + nPadd + 80*nHeaderLines)))

nChanSize = nblocsize/obsnchan
TotCenFreq = sum(cenfreq) / float(len(cenfreq))
TotBW = sum(obsbw)

if int(sum(NumBlocs)/len(NumBlocs)) != int(NumBlocs[0]):
	print("all files don''t have the same number of blocks...")
	sys.exit()
else:
	NumBlocsSpliced = NumBlocs[0]

IdxFiles = numpy.argsort(cenfreq)
if TotBW < 0:
	IdxFiles = IdxFiles[::-1]

TotBlocSize = int(nblocsize*len(IdxFiles))
NewTotBlocSize = int(TotBlocSize / float(sys.argv[2]))
TotNumChann = int(obsnchan * len(IdxFiles))

output_file = open(sys.argv[3],"wb")
for nblock in range(int(NumBlocs[0])):
	print "copy block #" + str(nblock+1) + "/" + str(int(NumBlocs[0]))
	for nDivid in range(int(sys.argv[2])):
		fread = open(list_files[0],'rb')	# open first file of data set
		fread.seek(int(nblock*(80*nHeaderLines+nPadd+nblocsize)))	# goes to the header
		currline = fread.read(80)
		output_file.write(currline)
		while str(currline[0:3]) != 'END':		# until reaching end of header
			currline = fread.read(80)		# read new header line
			if str(currline[0:9]) == 'BANKNAM =':
				teststr = 'BANKNAM = ''BLP00-37'''
				teststr = teststr + ' '*(80-len(teststr))
				currline = teststr
			if str(currline[0:9]) == 'OBSFREQ =':	# change central frequency value
				NewVal = TotCenFreq
				NewValStr = str(NewVal)
				if len(NewValStr) > 20:
					NewValStr = NewValStr[0:20]
				teststr = currline[0:9] + ' '*(20+1-len(NewValStr)) + NewValStr
				teststr = teststr + ' '*(80-len(teststr))
				currline = teststr
			if str(currline[0:9]) == 'OBSBW   =':	# change bandwidth value
				NewVal = TotBW
				NewValStr = str(NewVal)
				if len(NewValStr) > 20:
					NewValStr = NewValStr[0:20]
				teststr = currline[0:9] + ' '*(20+1-len(NewValStr)) + NewValStr
				teststr = teststr + ' '*(80-len(teststr))
				currline = teststr
			if str(currline[0:9]) == 'OBSNCHAN=':	# change number of coarse channels
				NewVal = TotNumChann
				NewValStr = str(NewVal)
				if len(NewValStr) > 20:
					NewValStr = NewValStr[0:20]
				teststr = currline[0:9] + ' '*(20+1-len(NewValStr)) + NewValStr
				teststr = teststr + ' '*(80-len(teststr))
				currline = teststr
			if str(currline[0:9]) == 'DIRECTIO=':	# change directio value
				NewVal = 0
				NewValStr = str(NewVal)
				if len(NewValStr) > 20:
					NewValStr = NewValStr[0:20]
				teststr = currline[0:9] + ' '*(20+1-len(NewValStr)) + NewValStr
				teststr = teststr + ' '*(80-len(teststr))
				currline = teststr
			if str(currline[0:9]) == 'BLOCSIZE=':	# change block size value
				NewVal = int(NewTotBlocSize)
				NewValStr = str(NewVal)
				if len(NewValStr) > 20:
					NewValStr = NewValStr[0:20]
				teststr = currline[0:9] + ' '*(20+1-len(NewValStr)) + NewValStr
				teststr = teststr + ' '*(80-len(teststr))
				currline = teststr
			if str(currline[0:9]) == 'NPKT    =':
				NewVal = int(NewTotBlocSize/nPktSize)
				NewValStr = str(NewVal)
				if len(NewValStr) > 20:
					NewValStr = NewValStr[0:20]
				teststr = currline[0:9] + ' '*(20+1-len(NewValStr)) + NewValStr
				teststr = teststr + ' '*(80-len(teststr))
				currline = teststr
			if str(currline[0:9]) == 'PKTIDX  =':
				NewVal = TotBlocSize/nPktSize*nblock + NewTotBlocSize/nPktSize*nDivid
				NewValStr = str(NewVal)
				if len(NewValStr) > 20:
					NewValStr = NewValStr[0:20]
				teststr = currline[0:9] + ' '*(20+1-len(NewValStr)) + NewValStr
				teststr = teststr + ' '*(80-len(teststr))
				currline = teststr
			if str(currline[0:9]) == 'PKTSTOP =':
				NewVal = TotBlocSize/nPktSize*(NumBlocsSpliced-1) + NewTotBlocSize/nPktSize*(int(sys.argv[2])-1)
				NewValStr = str(NewVal)
				if len(NewValStr) > 20:
					NewValStr = NewValStr[0:20]
				teststr = currline[0:9] + ' '*(20+1-len(NewValStr)) + NewValStr
				teststr = teststr + ' '*(80-len(teststr))
				currline = teststr
			output_file.write(currline)
		for nChan in range(int(obsnchan)):
			fread.seek(nblock*(nHeaderLines*80+nPadd+nblocsize)+nHeaderLines*80+nPadd+nChan*nChanSize+nDivid*nChanSize/int(sys.argv[2]))
			tmpdata = fread.read(int(nChanSize/int(sys.argv[2])))	# read data block
			output_file.write(tmpdata)	# write data block
		fread.close()			# close current file
		for nFile in range(1,numfiles):
			fread = open(list_files[nFile],'rb')	# open file
			for nChan in range(int(obsnchan)):
				fread.seek(nblock*(nHeaderLines*80+nPadd+nblocsize)+nHeaderLines*80+nPadd+nChan*nChanSize+nDivid*nChanSize/int(sys.argv[2]))
				tmpdata = fread.read(int(nChanSize/int(sys.argv[2])))	# read data block
				output_file.write(tmpdata)	# write data block
			fread.close()			# close current file
output_file.close()
