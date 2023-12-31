import re
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.animation
import time
import random
import numpy as np
import xarray as xr
import netCDF4 as nc
from datetime import datetime

stringText = ''
testEvent = "201500019" #gute testnummer: 201500019
eventLength = 0
currEventSpace = 0
selectedPlot = [0, 0]
lonVals = [0] * 100
latVals = [0] * 100
dateVals = [0] * 100
miniTestCounter = 0

#Open File
with open('testCoord.txt', 'r') as f:
    lines = f.readlines()

#Remove first 2 Lines
del lines[0]
del lines[0]

#Replace Spaces
lines = [line.replace(' ', ',') for line in lines]

for x in lines:
    stringText += x

#Split String
stringTextSplit = re.split(r',|\n', stringText)

#Filter String
def removeEmptyStrings(element):
    if element == '':
        return False
    
    return True
def removeZero(element):
    if element == 0:
        return False
    
    return True

filteredTextTemp = filter(removeEmptyStrings, stringTextSplit)
filteredText = list(filteredTextTemp)

#Get Lon,Lat from specific Event
for i in range(len(filteredText)):
    if filteredText[i] == "Event:":
        if filteredText[i+1] == testEvent: #Found Correct Event
            currEventSpace = i+1 #Holds current place of event number
            eventLength = int(filteredText[i+5]) #Number of plot points in event
            break
    if i == len(filteredText) - 1:
        print("Event Nummer wurde nicht gefunden.")
        quit()  

tickIndex = currEventSpace + 15
if filteredText[currEventSpace] == testEvent:
    for x in range(eventLength):
        lonVals[x] = filteredText[tickIndex]
        latVals[x] = filteredText[tickIndex+1]
        tickIndex += 17

#Get dates from specific Event
tickIndex2 = currEventSpace + 11
if filteredText[currEventSpace] == testEvent:
    for x in range(eventLength):
        dateVals[x] = filteredText[tickIndex2]
        tickIndex2 += 17
dateValsTrimmed = np.trim_zeros(dateVals)

#Filter empty array elements
lonValsFiltered = filter(removeZero, lonVals)
lonValsFilteredList = list(lonValsFiltered)
latValsFiltered = filter(removeZero, latVals)
latValsFilteredList = list(latValsFiltered)

#Convert to float
for i in range(0, len(lonValsFilteredList)):
    lonValsFilteredList[i] = float(lonValsFilteredList[i])

for i in range(0, len(latValsFilteredList)):
    latValsFilteredList[i] = float(latValsFilteredList[i])

#Plot Result
def plotting():
    fig = plt.figure(figsize=(12,9))
    currMarkerPoint = 0
    #m = Basemap(projection = 'mill', llcrnrlat = -90, urcrnrlat = 90, llcrnrlon = -180, urcrnrlon = 180, resolution = 'c')
    m = Basemap(projection = 'mill',
            llcrnrlat = latValsFilteredList[0] - 20,
            llcrnrlon = lonValsFilteredList[0] - 20,
            urcrnrlat = latValsFilteredList[eventLength-1] + 25,
            urcrnrlon = lonValsFilteredList[eventLength-1] + 37.5,
            resolution = 'i')

    # convert lon to correct values
    correctedLonValsFilteredList = lonValsFilteredList
    #correctedLatValsFilteredList = latValsFilteredList
    for i in range(len(correctedLonValsFilteredList)):
        correctedLonValsFilteredList[i] = (correctedLonValsFilteredList[i] + 180) % 360 - 180
    
    #Animate
    for k in range(1000):
        plt.clf()

        # drawing the coastline
        m.drawcoastlines()
        m.drawcountries(color='black')
        m.drawstates(color='black')
        m.drawmapboundary(fill_color='aqua')
        m.fillcontinents(color='coral', lake_color='aqua')

        #Draw wind map
        ds = xr.open_dataset('wind_2015-2016.nc') #path to .nc file

        windData = ds.variables['wind'][:]
        windLats = ds.variables['lat'][:]
        windLons = ds.variables['lon'][:]
        windTimes = ds.variables['time'][:]

        #correcting and sorting lon values for correct plotting
        windLonsLength = len(windLons)
        for x in range(windLonsLength):
            windLons.values[x] = (windLons.values[x] + 180) % 360 - 180
        
        windLons.values.sort()

        # plotting the wind map
        lon, lat = np.meshgrid(windLons, windLats)
        windX, windY = m(lon, lat)

        # transforming specific date to useable time for sel function
        currDate = dateValsTrimmed[currMarkerPoint]
        currDateTweaked = currDate[:4] + "-" + currDate[4:6] + "-" + currDate[6:8] + "T" + currDate[8:10] + ":00:00"

        c_scheme = m.pcolor(windX, windY, np.squeeze(ds.wind.sel(time=currDateTweaked)), cmap = 'jet')
        cbar = m.colorbar(c_scheme, location = 'right', pad = '10%')

        # plotting the map
        m.scatter(lonValsFilteredList, latValsFilteredList, latlon = True, s = 50, c = 'red', marker = 'X', alpha = 1)

        # draw line
        x, y = m(correctedLonValsFilteredList, latValsFilteredList)
        m.plot(x, y, '-', color = 'red', markersize = 5, linewidth = 1.5)

        plt.annotate('Event: ' + testEvent + '   ' + 'Marker Lon: ' + str(round(correctedLonValsFilteredList[currMarkerPoint], 2)) + ' ' + 'Marker Lat: ' + str(latValsFilteredList[currMarkerPoint]), xy=(0, 1), xycoords='axes fraction')

        selectedPlot[0] = correctedLonValsFilteredList[currMarkerPoint]
        selectedPlot[1] = latValsFilteredList[currMarkerPoint]
        currMarkerPoint += 1

        if (currMarkerPoint > len(correctedLonValsFilteredList)-1):
            currMarkerPoint = 0

        # draw green marker
        m.scatter(selectedPlot[0], selectedPlot[1], latlon = True, s = 500, c = 'green', marker = 'o', alpha = 0.8)
        plt.waitforbuttonpress()

    plt.show()
    
plotting()

#Write File
#with open('testCoord.txt', 'w') as f:
#    f.writelines(lines)