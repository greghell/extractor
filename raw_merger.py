import os
import glob
import sys
import math
import numpy
import subprocess

os.chdir(sys.argv[1])					# change directory
list_files = os.listdir(sys.argv[1])	# list all files from the data set
numfiles = len(list_files)				# counts number of files in dataset

if numfiles == 0:
	print("error : no file corresponding to the dataset indicated")
	sys.exit()
else:
	print "there are " + str(numfiles) + " files in the data set"

idx = -1
cenfreq = [0]*numfiles	# array of central frequencies to order files
NodeNum = [0]*numfiles	# array of compute node ID

for fname in list_files:
	idx = idx + 1
	fread = open(fname,'rb')	# open first file of data set
	currline = str(fread.read(80))		# reads first line
	nHeaderLines = 1
	while currline[0:3] != 'END':		# until reaching end of header
		currline = str(fread.read(80))	# read new header line
		if currline[0:9] == 'OBSFREQ =':	# read cenral frequency
			cenfreq[idx] = float(currline[9:])
		if currline[0:9] == 'OBSNCHAN=':	# read number of coarse channels
			obsnchan = int(currline[9:])
		if currline[0:9] == 'DIRECTIO=':	# read directio flag
			ndirectio = int(currline[9:])
		if currline[0:9] == 'BLOCSIZE=':	# read block size
			nblocsize = int(currline[9:])
		if currline[0:9] == 'BANKNAM =':
			NodeNum[idx] = int(currline[14:16])
		nHeaderLines = nHeaderLines + 1		# counts number of lines in header
	fread.close()
nPadd = 0
if ndirectio == 1:
	nPadd = int((math.floor(80.*nHeaderLines/512.)+1)*512 - 80*nHeaderLines)
statinfo = os.stat(fname)
NumBlocs = int(round(statinfo.st_size / (nblocsize + nPadd + 80*nHeaderLines)))
nChanSize = nblocsize / obsnchan

dirname = "merged_raw_files"
	
for idx in range(numfiles):
	for idx2 in range(idx,numfiles):
		if cenfreq[idx] == cenfreq[idx2] and idx != idx2:
			print "merging node #" + str(NodeNum[idx]) + " and node #" + str(NodeNum[idx2])

			if NodeNum[idx] < NodeNum[idx2]:
				fLow = list_files[idx]
				fHigh = list_files[idx2]
			else:
				fLow = list_files[idx2]
				fHigh = list_files[idx]
			
			fMerged = fLow
			fMerged = fMerged.replace(".raw","")
			fMerged = fMerged + "_merged.raw"
			
			print "new file is " + fMerged
			output_file = open(fMerged,"wb")
			freadLow = open(fLow,'rb')	# open first file of data set
			freadHigh = open(fHigh,'rb')	# open second file of data set

			for nblock in range(NumBlocs):
				freadLow.seek(int(nblock*(80*nHeaderLines+nPadd+nblocsize)))
				currline = freadLow.read(80)
				output_file.write(currline)
				while str(currline[0:3]) != 'END':		# until reaching end of header
					currline = freadLow.read(80)		# read new header line
					output_file.write(currline)
				for nChan in range(obsnchan/2):
					freadLow.seek(int(nblock*(80*nHeaderLines+nPadd+nblocsize)) + nChan*nChanSize,os.SEEK_SET)
					data = freadLow.read(nChanSize)
					output_file.write(data)
				for nChan in range(obsnchan/2,obsnchan):
					freadHigh.seek(int(nblock*(80*nHeaderLines+nPadd+nblocsize)) + nChan*nChanSize,os.SEEK_SET)
					data = freadHigh.read(nChanSize)
					output_file.write(data)
					
			output_file.close()
			freadLow.close()
			freadHigh.close()
			if not os.path.isdir(dirname):
				subprocess.call(["sudo","mkdir",dirname])
			subprocess.call(["sudo","mv",fLow,dirname+"/"+fLow])
			subprocess.call(["sudo","mv",fHigh,dirname+"/"+fHigh])
					
					