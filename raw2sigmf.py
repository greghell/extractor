# first argument = .RAW filename of one raw file of the data set
# second argument = frequency within coarse channel to extract
# add check for number of arguments
# remember uncommenting arguments fname and fFreq
# right now does not work for anything else than ci8

import glob
import numpy as np
import os
import math
import sys
import json

fname = sys.argv[1]
fFreq = float(sys.argv[2])

# make sure of right number of arguments
#if len(sys.argv) != 4:
#sys.exit()

if (fname[-4:] == '.raw'):
    fname = fname.replace(fname[len(fname)-8:],"*.raw")
else:
    print("enter raw file name\n")
    sys.exit()

all_filenames = sorted(glob.glob(fname))    # list of all files in RAW dataset

# read 1st header from 1st file in data set
fname = all_filenames[0]
fread = open(fname,'r')        # open first file of data set
currline = str(fread.read(80))          # reads first line
nHeaderLines = 1
headr = []
while currline[0:3] != 'END':           # until reaching end of header
    currline = str(fread.read(80))  # read new header line
    if currline[0:9] == 'PKTSIZE =':	# read packet size
        nPktSize = float(currline[9:])
    if currline[0:9] == 'OBSFREQ =':        # read cenral frequency
        cenfreq = float(currline[9:])
    if currline[0:9] == 'OBSBW   =':        # read bandwidth
        obsbw = float(currline[9:])
    if currline[0:9] == 'OBSNCHAN=':        # read number of coarse channels
        obsnchan = float(currline[9:])
    if currline[0:9] == 'DIRECTIO=':        # read directio flag
        ndirectio = float(currline[9:])
    if currline[0:9] == 'BLOCSIZE=':        # read block size
        nblocsize = float(currline[9:])
    if currline[0:9] == 'NBITS   =':        # read bit-depth
        nbits = int(currline[9:])
    if currline[0:9] == 'DAQPULSE=':        # read time and date of observation
        timedate = str(currline[9:])
        timedate = timedate.strip()
    if currline[0:9] == 'SRC_NAME=':        # read name of tracked source
        source = str(currline[9:])
        source = source.strip()
    if currline[0:9] == 'TELESCOP=':        # read name of instrument
        telescope = str(currline[9:])
        telescope = telescope.strip()
    nHeaderLines = nHeaderLines + 1         # counts number of lines in header
    headr.append(currline)
fread.close()

nChanSize = int(nblocsize / obsnchan)   # size of 1 channel per block in bytes
nPadd = 0
if ndirectio == 1:
    nPadd = int((math.floor(80.*nHeaderLines/512.)+1)*512 - 80*nHeaderLines)    # calculate directIO padding
statinfo = os.stat(fname)
NumBlocs = int(round(statinfo.st_size / (nblocsize + nPadd + 80*nHeaderLines)))

# frequency coverage of dataset
fLow = cenfreq - obsbw/2.
fHigh = cenfreq + obsbw/2.
dChanBW = obsbw/obsnchan

# make sure user asks for frequency covered by file
if fFreq < min(fLow,fHigh) or fFreq > max(fLow,fHigh):
    print("Frequency not covered by file")
    print("Frequency bandwidth = ["+str(min(fLow,fHigh))+","+str(max(fLow,fHigh))+"]")
    sys.exit()

# calculate what channel number to extract
if obsbw > 0:
    nChanOI = int((fFreq-fLow)/dChanBW)
else:
    nChanOI = int((fLow-fFreq)/abs(dChanBW))
    
BlocksPerFile = np.zeros(len(all_filenames))
idx = 0
for fname in all_filenames:
    statinfo = os.stat(fname)
    BlocksPerFile[idx] = int(statinfo.st_size / (nblocsize + nPadd + 80*nHeaderLines))
    idx = idx+1

NumBlockTotal = int(sum(BlocksPerFile))
NewTotBlocSize = int(NumBlockTotal * nChanSize)

# extracted channel frequency coverage
fLowChan = fLow + (nChanOI)*dChanBW
fHighChan = fLowChan + dChanBW
TotCenFreq = (fLowChan+fHighChan)/2.
print("extracting channel #"+str(nChanOI))
print("frequency coverage = "+str(min(fLowChan,fHighChan))+" - "+str(max(fLowChan,fHighChan))+" MHz")

ofname_meta1 = fname.split('\\')[-1][:-14]+"_pol1.sigmf-meta"     # meta file name pol#1
ofname_data1 = fname.split('\\')[-1][:-14]+"_pol1.sigmf-data"     # data file name pol#1
ofname_meta2 = fname.split('\\')[-1][:-14]+"_pol2.sigmf-meta"     # meta file name pol#2
ofname_data2 = fname.split('\\')[-1][:-14]+"_pol2.sigmf-data"     # data file name pol#2

# extract and write data to file
output_file1 = open(ofname_data1,'wb')
output_file2 = open(ofname_data2,'wb')
idx = -1
for fname in all_filenames:
    idx = idx+1
    fread = open(fname,'rb')
    print("extract data from "+fname.split('\\')[-1])
    for nblock in range(int(BlocksPerFile[idx])):
        fread.seek(int(nblock*(nHeaderLines*80+nPadd+nblocsize)+nHeaderLines*80+nPadd+nChanOI*nChanSize))
        tmpdata = np.fromfile(fread, dtype=np.int8, count=int(nChanSize))
        tmpdata = np.reshape(tmpdata,(2,int(nChanSize/2)),order='F')
        output_file1.write(np.reshape(tmpdata[:,::2],(1,int(nChanSize/2)),order='F'))    # write pol 1
        output_file2.write(np.reshape(tmpdata[:,1::2],(1,int(nChanSize/2)),order='F'))    # write pol 2
    fread.close()
output_file1.close()
output_file2.close()

# make meta data files

dataset_format = "ci"+str(nbits)+"_be"

meta1 = {
"global": [
{"core:datatype" : dataset_format,
"core:version" : "0.0.1",
"core:sample_rate" : dChanBW*1e6,
"core:hw" : telescope,
"core:description" : "converted from GUPPI RAW - source observed : "+source,
"core:extensions" : {
"antenna" : "v0.9.0"
},
"antenna:low_frequency" : min(fLowChan,fHighChan),
"antenna:high_frequency" : max(fLowChan,fHighChan),
"antenna:cross_polar_discrimination" : "polarization XX",
"antenna:version" : "v0.9.0"
}
],
"captures": [
{
"core:sample_start" : 0,
"core:frequency" : TotCenFreq*1e6,
"core:datetime" : timedate
}
],
"annotations": [
]
}

meta2 = {
"global": [
{"core:datatype" : dataset_format,
"core:version" : "0.0.1",
"core:sample_rate" : dChanBW*1e6,
"core:hw" : telescope,
"core:description" : "converted from GUPPI RAW - source observed : "+source,
"core:extensions" : {
"antenna" : "v0.9.0"
},
"antenna:low_frequency" : min(fLowChan,fHighChan),
"antenna:high_frequency" : max(fLowChan,fHighChan),
"antenna:cross_polar_discrimination" : "polarization YY",
"antenna:version" : "v0.9.0"
}
],
"captures": [
{
"core:sample_start" : 0,
"core:frequency" : TotCenFreq*1e6,
"core:datetime" : timedate
}
],
"annotations": [
]
}

fopen1 = open(ofname_meta1,'w')
fopen2 = open(ofname_meta2,'w')
fopen1.write(json.dumps(meta1))
fopen2.write(json.dumps(meta2))
fopen1.close()
fopen2.close()

