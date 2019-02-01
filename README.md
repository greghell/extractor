## extractor

# extract_blocks.py
Python scripts that extracts a few blocks of data from a RAW file data set and create a new RAW file.  
Usage:  
[1] path to files  
[2] repeating part in file names  
[3] starting time in s  
[4] stopping time in s  
[5] path to extract the data to  


# raw_merger.py
Some compute nodes overlap exactly. raw_merger.py merges together raw files covering the same frequency bandwidth but with different compute nodes (merges 32 coarse channels of one, and 32 coarse channels of the other).  
Usage:  
[1] directory containing the RAW file data set  

# splicer_raw.py  
Python script splicing RAW file data sets after block extraction.  
Usage:  
[1] path to directory containing all raw files to be spliced  
[2] divider (divides data blocks by this integer number for software support)  
[3] output file name  

# RAWchannel_extractor.py
Python script extracting one unique coarse channel out of a RAW file dataset, and writes it in a new RAW file  
Usage:  
[1] input file name (any file from the dataset)  
[2] frequency included in the coarse channel to extract  
[3] output file name (don't forget '.raw')

# raw2sigmf.py
Python scripts that converts 1 coarse channel of a raw file into a SigMF format.
Usage:
[1] name of 1 raw file of a .raw dataset
[2] frequency of interest
