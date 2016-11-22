import urllib
import os
import csv
import json
import geopy
import pprint
import sys
import matplotlib
import matplotlib.pyplot as plt
import scipy.stats as stat
import numpy as np
from geopy.distance import vincenty

# turn downloading of new data from server on or off:
download = False

# some constants:
circleRadius = 100
idwNeighbors = 5
# these are used to correct for the shift in the click data
# (error introduced during reverse transformation of click locations)
shiftlat = -0.0018
shiftlon = 0.0025




# some helper functions:

# loads all test data into one big dictionary:
def loadData():
    responses = []
    if download:
        # download the CSV with the up-to-date interview responses to have a backup
        response = urllib.urlopen(
            "http://carsten.io/uncertainty/experiments/questionnaires.csv")

        # download csv to string
        text = response.read()

        # fix formatting of csv:
        text = text.replace(", ", ",").replace(",\n", "\n")

        # save to local file as backup:
        with open("questionnaires.csv", "w") as text_file:
            text_file.write(text)




    # then read in the local csv file as dict
    with open("questionnaires.csv", 'rb') as csvfile:
        # r = csv.reader(csvfile, delimiter=',', quotechar='|')
        rs = csv.DictReader(csvfile, delimiter=',')
        for r in rs:
            responses.append(r)


    # next, go through all the sessions and check if we already have a copy of the data for that session;
    # if not, download the data:
    if download:
        for r in responses:
            if not os.path.exists(str(r["session"])):
                print "Downloading new data for session " + str(r["session"]) + "..."
                os.makedirs(str(r["session"]))
                for i in range(1, 12):
                    path = str(r["session"]) + "/" + str(i) + ".json"
                    urllib.urlretrieve(
                        "http://carsten.io/uncertainty/experiments/" + path, path)
                    path = str(r["session"]) + "/log.txt"
                    urllib.urlretrieve(
                        "http://carsten.io/uncertainty/experiments/" + path, path)



    # now transform the dict so that the session becomes the key:
    temp = dict()

    for r in responses:
        temp[r["session"]] = r

    responses = temp
    temp = None


    # next, add the log file data to the dict:
    for session in responses:
        # add the log file values to the dict:
        responses[session]['pages'] = dict()

        logfile = session + '/log.txt'

        with open(logfile) as f:
            lines = f.readlines()

            for l in lines:
                parts = l.split(', ')

                # name the parts:
                page = parts[0]
                time = int(parts[1])
                lon = float(parts[2]) + shiftlon # shift correction!
                lat = float(parts[3]) + shiftlat # shift correction!

                responses[session]['pages'][page] = dict()
                responses[session]['pages'][page]['time'] = time
                responses[session]['pages'][page]['clicklat'] = lat
                responses[session]['pages'][page]['clicklon'] = lon

                # and attach the geojson for this page:
                with open(session+'/'+page+'.json') as geojson_file:
                    geojson = json.load(geojson_file)

                responses[session]['pages'][page]['geojson'] = geojson


    # check completeness

    print "n = " + str(len(responses))

    for session in responses:

        pages = responses[session]['pages']

        for i in range(1,12):
            if str(i) not in pages:
                print session + " lacks page " + str(i)

            keys = ['time', 'clicklat', 'clicklon', 'geojson']

            for page in pages:
                p = pages[page]
                for key in keys:
                    if key not in p:
                        print session + ", page " + str(i) + " lacks " + key


    return responses




# calculates the vincenty distance between A and B with x,y coordinates
def getDist(pointA, pointB):
    # geojson uses x/y, geopy uses lat/lon, so we have to flip the coordinates:
    return vincenty((pointA[1], pointA[0]), (pointB[1], pointB[0])).meters


# counts the occurances of a certain key in a dictionary (dic).
def gatherPieData(dic, key):
    labels = []
    counts = []
    for session in dic:
        if dic[session][key] in labels:
            i = labels.index(dic[session][key])
            counts[i] = counts[i] + 1
        else:
            labels.append(dic[session][key])
            counts.append(1)

    return sortCounts(labels, counts)

# puts the labels and corresponding counts in alphabetic order
def sortCounts(labels, counts):
    newlabels = []
    newcounts = []

    # add leading zeros so that the sorting works:
    for i in range(len(labels)):
        if len(labels[i]) == 1:
            labels[i] = "0" + labels[i]

    # repeat until the input list is empty:
    while labels:
        i = labels.index(min(labels))
        newlabels.append(labels[i])
        newcounts.append(counts[i])
        del labels[i]
        del counts[i]

    # remove leading zeros again:
    for i in range(len(newlabels)):
        if newlabels[i][0] == "0":
            newlabels[i] = newlabels[i][1]

    return newlabels, newcounts



# sorts A and B in ascending order of A
def sortBoth(a, b):
    newa = []
    newb = []

    # repeat until the input list is empty:
    while a:
        i = a.index(min(a))
        newa.append(a[i])
        newb.append(b[i])
        del a[i]
        del b[i]

    return newa, newb





def openGeoJSON(responses, session, page):
    return responses[session]['pages'][str(page)]['geojson']

# Returns the coordinates of the first point with the given
# accurracy value. Only really useful for values 1 and 7,
# which only appear once in the data.
def getCoordsByValue(responses, session, page, value):
    data = openGeoJSON(responses, session, page)
    for feature in data['features']:
        # Careful here: high accuracy values actually mean high uncertainty.
        # Don't ask me why I did it that way...
        if feature['properties']['accuracy'] == value:
            return feature['geometry']['coordinates']

    # return an empty array if no point with accuracy of 'value' is found,
    # which should never happen
    print "No point found... this shouldn't happen!"
    return []


def getMostUncertain(responses, session, page):
    return getCoordsByValue(responses, session, page, 7)


def getLeastUncertain(responses, session, page):
    return getCoordsByValue(responses, session, page, 1)


def getClosest(session, page, clickpoint):
    return getIDW(session, page, clickpoint, 1)

# dist defaults to circleRadius set at the top.
# 200m is roughly the real-world diameter of our circle in the test
def getNumOfPointsWithinDistance(session, page, clickpoint, maxDist=circleRadius):
    data = openGeoJSON(responses, session, page)
    distances = np.array([])
    for feature in data['features']:
        d = getDist(feature['geometry']['coordinates'], clickpoint)
        distances = np.append(distances, [d])

    return distances[distances <= maxDist].size


# gets an inverse distance weighted average uncertainty at clickpoint
# using its n nearest neighbors
def getIDW(session, page, clickpoint, n):
    data = openGeoJSON(responses, session, page)

    distances = np.array([])
    uncertainties = np.array([])

    # put all the distances in one array, and the accuracy values into another
    # one:
    for feature in data['features']:

        d = getDist(feature['geometry']['coordinates'], clickpoint)
        u = feature['properties']['accuracy']

        distances = np.append(distances, [d])
        uncertainties = np.append(uncertainties, [u])

    # get the indexes of the n smallest values:
    indexes = distances.argsort()[:n]

    # get the distances at those indexes and get the total:
    shortestN = distances[indexes]

    totaldist = np.sum(shortestN)
    weights = np.divide(shortestN, totaldist)
    weighted = np.multiply(uncertainties[indexes], weights)
    iwd = np.sum(weighted)

    return iwd





# ---- ---- ---- ---- ---- ---- ----
# let's start the actual work...
# ---- ---- ---- ---- ---- ---- ----

# load the data
os.chdir(os.path.expanduser("~") + "/Dropbox/Code/UncertD3/evaluation/data/")
responses = loadData()



# on to the actual analysis:
# first, some pie charts
matplotlib.style.use("fivethirtyeight")
ftecolors = ['#fc4f30', '#008fd5', '#e5ae38', '#6d904f', '#8b8b8b', '#810f7c']

# gender:

# gather the data
labels, counts = gatherPieData(responses, "gender")
total = sum(counts)

plt.pie(counts, labels=labels, colors=ftecolors, autopct=lambda(
    p): '{:.0f}'.format(p * total / 100), shadow=False, startangle=90)
# Set aspect ratio to be equal so that pie is drawn as a circle.
plt.axis('equal')
plt.suptitle('Gender breakdown')
plt.savefig("../plots/gender.pdf")

plt.clf()

# best and worst viz types

d = {"bestmost": "Best visualization to identify the most uncertain object",
     "bestleast": "Best visualization to identify the least uncertain object",
     "worstmost": "Worst visualization to identify the most uncertain object",
     "worstleast": "Worst visualization to identify the least uncertain object"}

colors = ['#008fd5', '#33bbff', '#005f8f', '#fc4322', '#B51D03', '#FB310E',
          '#DD2403', '#C92103', '#fc4f30', '#A11A02', '#F12704', '#8b8b8b']

for key, value in d.iteritems():

    labels, counts = gatherPieData(responses, key)

    for i in range(len(labels)):
        labels[i] = labels[i].replace("Please select...", "undecided")

    total = sum(counts)

    plt.pie(counts, labels=labels, colors=colors, autopct=lambda(
        p): '{:.0f}'.format(p * total / 100), shadow=False, startangle=90)

    plt.axis('equal')
    plt.suptitle(value)
    plt.savefig("../plots/" + key + ".pdf")

    plt.clf()


# age box plot:
ages = []
for session in responses:
    ages.append(int(responses[session]["age"]))

plt.boxplot(ages)
plt.suptitle("Age distribution")
plt.savefig("../plots/age.pdf")

plt.clf()


#print some stats
print "Mean age: "+str(np.mean(ages))
print "Std dev.: "+str(np.std(ages))
print "Min age: "+str(np.min(ages))
print "Max age: "+str(np.max(ages))


# Let's take a look at the GeoJSON files and click locations. First, load
# the click logs:

distances = [[],[],[],[],[],[],[],[],[],[],[]]
distances_no = [[],[],[],[],[],[],[],[],[],[],[]] # collect just the data that are no outliers
clostests = [[],[],[],[],[],[],[],[],[],[],[]]
clostests_no = [[],[],[],[],[],[],[],[],[],[],[]] # collect just the data that are no outliers
idws = [[],[],[],[],[],[],[],[],[],[],[]]
idws_no = [[],[],[],[],[],[],[],[],[],[],[]] # collect just the data that are no outliers
idwsWithinDistance = [[],[],[],[],[],[],[],[],[],[],[]]
rspTimes = [[],[],[],[],[],[],[],[],[],[],[]]
rspTimes_no = [[],[],[],[],[],[],[],[],[],[],[]]




lostclicks = 0

# go through all sessions:
for session in responses:
    s = responses[session]
    for p in range(1,12):
        page = str(p)
        # the uneven pages ask for the MOST uncertain object,
        # the even pages for the LEAST uncertain object

        clickpoint = [s['pages'][page]['clicklon'], s['pages'][page]['clicklat']]
        page = int(page)

        if page % 2 == 0:  # even
            # look for the least uncertain object in the corresponding geojson
            maxP = getLeastUncertain(responses, session, page)
        else:  # not even
            # look for the most uncertain object in the corresponding geojson
            maxP = getMostUncertain(responses, session, page)

        # and calculate the distance to the click
        d = getDist(maxP, clickpoint)

        # collect all distances in a list of lists by page
        # our pages start at 1, but the list indices at zero, so always
        # subtract 1:
        distances[page - 1].append(d)
        if d < circleRadius:
            distances_no[page - 1].append(d)

        # add the response time:

        time = s['pages'][str(page)]['time']

        # set the max response time to 60 seconds, otherwise the box plots become useless:
        if time > 60000:
            time = 60000

        # change from milliseconds to seconds:
        time = time/1000.0

        rspTimes[page - 1].append(time)
        if d < circleRadius:
            rspTimes_no[page - 1].append(time)

        # collect all uncertainty values in a list of lists by page
        # look for the closest point to the click and check its uncertainty
        c = getClosest(session, page, clickpoint)
        clostests[page - 1].append(c)
        if d < circleRadius:
            clostests_no[page - 1].append(c)

        # collect all IDW values in a list of lists by page
        idw = getIDW(session, page, clickpoint, idwNeighbors)
        idws[page - 1].append(idw)
        if d < circleRadius:
            idws_no[page - 1].append(idw)

        # collect all IDW values for clicks that are within 200m of our track
        n = getNumOfPointsWithinDistance(session, page, clickpoint)
        if n > 0:
            idw = getIDW(session, page, clickpoint, n)
            idwsWithinDistance[page - 1].append(idw)
        else:
            lostclicks = lostclicks + 1

print str(lostclicks) + " out of " + str(len(responses)*11) + " outside of " + str(circleRadius) + "m circle (" + str(lostclicks/len(responses)*10.0) + "%)."

# box plots of the response times
plt.boxplot(rspTimes)
plt.suptitle("Response times per test page in seconds")
plt.savefig("../plots/responsetimes.pdf")

plt.clf()

plt.boxplot(rspTimes_no)
plt.suptitle("Response times per test page in seconds (no outliers)")
plt.savefig("../plots/responsetimes_no.pdf")

plt.clf()


# make a box plot of the distances:
plt.boxplot(distances)
plt.suptitle("Distances")
plt.savefig("../plots/distances.pdf")

plt.clf()

# the same without outliers:
plt.boxplot(distances_no)
plt.suptitle("Distances (no outliers)")
plt.savefig("../plots/distances_no.pdf")

plt.clf()


# and one of the uncertainty values of the closest points:
plt.boxplot(clostests)
plt.suptitle("Uncertainty of closest point")
plt.savefig("../plots/clostest.pdf")

plt.clf()

# the same without outliers:
plt.boxplot(clostests_no)
plt.suptitle("Uncertainty of closest points (no outliers)")
plt.savefig("../plots/clostest_no.pdf")

plt.clf()


# and another one, this time with IDW(5):
plt.boxplot(idws)
plt.suptitle("IDW uncertainty of 5 closest points")
plt.savefig("../plots/idw5.pdf")

plt.clf()

# the same without outliers:
plt.boxplot(idws_no)
plt.suptitle("IDW uncertainty of 5 closest points  (no outliers)")
plt.savefig("../plots/idw5_no.pdf")

plt.clf()


# and another IDW one, this time only looking at clicks that have points within the circle:
plt.boxplot(idwsWithinDistance)
plt.suptitle("IDW uncertainty of points within circle")
plt.savefig("../plots/idw-within-circle.pdf")

plt.clf()




# pie plots of the answers to the rest of the questionnaire:

plts = ["size", "sizeinter", "transparency", "transparencyinter", "movement", "movementinter", "combined", "job"]
questions = ['In the visualizations that used varying symbol sizes, I was under the impression that symbol size reflects...', 'In my interpretation, larger symbols reflect...', 'In the visualizations that used varying transparency, I was under the impression that transparency reflects...', 'In my interpretation, more transparent symbols reflect...', 'In the visualizations that used movement, I was under the impression that movement reflects...', 'In my interpretation, more movement reflects...', 'In my interpretation, the visualizations that combined at least two of these (size, transparency, movement) ...', 'You deal with maps, GIS, etc. at work and/or college']

for i in range(len(plts)):
    labels, counts = gatherPieData(responses, plts[i])
    total = sum(counts)

    plt.pie(counts, labels=labels, colors=ftecolors, autopct=lambda(
        p): '{:.0f}'.format(p * total / 100), shadow=False, startangle=90)

    plt.axis('equal')
    plt.suptitle(questions[i])
    plt.savefig("../plots/"+plts[i]+".pdf")

    plt.clf()



# simple scatter plot of response time vs. distance to correct answer:

for page in range(len(distances)):

    print "Pearson's r for page " + str(page) + ": " + str(stat.pearsonr(distances[page], rspTimes[page]))

    d, t = sortBoth(distances[page], rspTimes[page])

    # these have to be np arrays, see http://stackoverflow.com/questions/26690480/matplotlib-valueerror-x-and-y-must-have-same-first-dimension
    d = np.array(d)
    t = np.array(t)

    m, b = np.polyfit(t, d, 1)

    plt.plot(t, d, ".", label="Page "+str(page))
    plt.plot(t, m*d + b, "-", linewidth = 1.0)

    plt.suptitle("Distance to correct answer vs. response time")
    plt.savefig("../plots/dist_vs_time_"+str(page+1)+".pdf")

    plt.clf()



    # and repeat without outliers:

    print "Pearson's r for page " + str(page) + ": " + str(stat.pearsonr(distances[page], rspTimes[page]))

    d, t = sortBoth(distances_no[page], rspTimes_no[page])

    d = np.array(d)
    t = np.array(t)

    m, b = np.polyfit(t, d, 1)

    plt.plot(t, d, ".", label="Page "+str(page))
    plt.plot(t, m*d + b, "-", linewidth = 1.0)

    plt.suptitle("Distance to correct answer vs. response time")
    plt.savefig("../plots/dist_vs_time_"+str(page+1)+"_no.pdf")

    plt.clf()
