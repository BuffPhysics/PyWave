#                                                                                            #
# ========================================================================================== #
# ========================================================================================== #
# ======================== Python Based Wavedump Processing Code =========================== #
# ========================================================================================== #
# ============================= Written by C. Awe - Feb 2019 =============================== #
# ========================================================================================== #
# ========================================================================================== #
#                                                                                            #

import random
import numpy as np
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
from array import array
from tqdm import tqdm

#Define constants
numSamples_per_wf = 8192 #Number of samples in each waveform.
ns_per_sample = 4 #Nanoseconds per sample.
dynamic_range = 4096 #Max ADC value of the digitizer.
bl_lower = 0 #Lower limit for collecting baseline data.
bl_upper = 1000 #Upper limit for collecting baseline data.
peak_low = 1500 #Lower limit for looking for a peak high value.
peak_high = 8192 #Upper limit for looking for a peak high value.

#Read in a file based on user input
def readInpFile():

	#Pretty standard file importing.
	#filename = input( "Enter the path to the raw wavedump file: " )
	filename = '/Volumes/BARCODE/wave0-2019-02-15-15-31-53.txt'
	file = open(filename,"r")
	text=file.read()
	file.close()
	return text

#Get the number of events in a file.
def getNumEvents( fileContents ):

	#Load in the text, find the number of samples and divide by samples/wf.
	samples = fileContents.split('\n')
	numLines = len(samples)
	return float( numLines / numSamples_per_wf )
	
#Fill a 2D array with all waveform.
def getWFs( fileContents, numEvents ):

	#Read in data and check the number of events.
	#fileContents = readInpFile()
	samples = fileContents.split('\n')
	
	#Make an empty array to hold our waveforms.
	wfs = []
	
	#Updated method populating a 2D array to speed up the code. 
	for k in range(0,int(numEvents)):
		event=[]
		for j in range(0,numSamples_per_wf):
			sample = float(samples[k*numSamples_per_wf+j])
			event.append(sample)
		wfs.append(event)

	return wfs

#Plot the waveform corresponding to the supplied event number.
def plotWaveform( wfs, eventNum ):

	#Check that our event number is in bounds
	if( eventNum >= 0 and eventNum < len(wfs) ):
		#Grab our waveform.
		wf = wfs[eventNum]
		
		#Plot it.
		plt.plot(wf, 'ro')
		plt.ylabel('ADC')
		plt.xlabel('Sample Number')
		#plt.axis([0, numSamples_per_wf, 0,500])
		ytick_arr = [] #array to hold y axis tick locations
		numyTicks = 8 #Number of ticks on the y axis.
		for i in range(1,numyTicks+1):
			ytick_arr.append(int(dynamic_range/numyTicks*i))
		plt.yticks(ytick_arr,ytick_arr) #Dynamic range of the DT5720
		plt.show()
	else:
		print("Event number out of bounds, aborting.")
	
#Compute a baseline value from the front of the waveform.
def getBaseline( wf ):
	dummy_arr = []
	#Fill an array with the baseline sample window of our waveform.
	for i in range(bl_lower,bl_upper):
		dummy_arr.append(wf[i])
		
	#Make an array to hold the baseline mean and rms
	bl_Info = []
	dumpy_arr = np.array(dummy_arr) #Make a dumb numpy array for convenience.
	mean = np.mean(dumpy_arr)
	rms = np.sqrt(np.mean(dumpy_arr**2))
	#print("Mean is: " + str(mean)) #Debug
	#print("RMS is: " + str(rms)) #Debug
	bl_Info.append(mean)
	bl_Info.append(rms)
	return bl_Info
	
#Find the peak high value in a specified region.
def getPeak( wf ):
	peak = 0
	peakTime = 0
	for i in range(peak_low,peak_high-1):
		if(wf[i] > peak):
			peak = wf[i]
			peakTime = i
	peakInfo = []
	peakInfo.append(peak)
	peakInfo.append(peakTime)
	return peakInfo

#Main function, this is the primary analysis script that runs automatically.		
def main():

	#Read in data and check the number of events.
	fileContents = readInpFile()
	samples = fileContents.split('\n')
	numEvents = getNumEvents( fileContents )
	print("Found "+str(int(numEvents))+" events. Processing...")
	wfs = getWFs( fileContents, numEvents )
	
	#Make arrays for our analysis results.
	bl_rms_arr = []
	bl_mean_arr = []
	peak_arr = []
	peak_time_arr = []
	
	#Step through each event, load the waveform and analyze it. Fill an array as we go.
	for i in range(0,int(numEvents)):
		#print(str(i)) #Debug
		wf = wfs[i]
		bl_Info=[]
		bl_Info = getBaseline( wf )
		bl_mean = bl_Info[0]
		bl_rms = bl_Info[1]
		peakInfo = []
		peakInfo = getPeak( wf )
		bl_rms_arr.append( bl_rms )
		bl_mean_arr.append( bl_mean )
		peak_arr.append( peakInfo[0] - bl_mean )
		peak_time_arr.append( peakInfo[1] )
		
	print("Processing finished, plotting...")
	
	#Plot whatever needs plotting.
	plt.subplot(221)
	plt.hist(bl_rms_arr,100)
	plt.xlabel('Baseline RMS (ADC)')
	plt.ylabel('Counts')
	plt.subplot(222)
	plt.hist(peak_arr,100)
	plt.xlabel('Peak Above Baseline (ADC)')
	plt.ylabel('Counts')
	plt.subplot(223)
	plt.hist(peak_time_arr,100)
	plt.xlabel('Peak Time (sample number)')
	plt.ylabel('Counts')
	#plt.yscale('log')
	plt.subplot(224)
	normalize = mpl.colors.Normalize(vmin=0,vmax=5)
	plt.hist2d(peak_time_arr,peak_arr,100,cmap='cubehelix_r',norm=normalize)
	plt.xlabel('Peak Time (sample number)')
	plt.ylabel('Peak Above Baseline (ADC)')
	plt.show()
	
	plotstatus = input( "Plot a random waveform? (y/n): " )
	while( plotstatus == 'y' ):
		randomEvent = random.randint(0,numEvents)
		print("Plotting event "+str(randomEvent))
		plotWaveform( wfs, randomEvent )
		plotstatus = input( "Plot a random waveform? (y/n): " )
		
#Execute main function 	
if __name__== "__main__":
  main()
		
		
		
		
		
		
		
		
		
		