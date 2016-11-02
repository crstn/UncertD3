import urllib, os, csv, matplotlib, json, geopy, pprint
import matplotlib.pyplot as plt
from geopy.distance import vincenty

# some helper functions:
def getDist(pointA, pointB):
    # geojson uses x/y, geopy uses lat/lon, so we have to flip the coordinates:
    return vincenty((pointA[1], pointA[0]), (pointB[1], pointB[0])).meters

# counts the occurances of a certain key in a dictionary (dic).
def gatherPieData(dic, key):
    labels = []
    counts = []
    for row in dic:
        if row[key] in labels:
            i = labels.index(row[key])
            counts[i] = counts[i] + 1
        else:
            labels.append(row[key])
            counts.append(1)

    return sortCounts(labels, counts)

# puts the labels and corresponding counts in alphabetic order
def sortCounts(labels, counts):
    newlabels = []
    newcounts = []

    # add leading zeros so that the sorting works:
    for i in range(len(labels)):
        if len(labels[i]) == 1:
            labels[i] = "0"+labels[i]

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

# The limit will cap the response time at x milliseconds in order not to screw up the box plots later.
# Default is 80 seconds.
def getresponsetimes(responses, limit = 80000):

    responsetimes = []

    for r in responses:
        logfile = str(r["session"])+'/log.txt'
        with open(logfile) as f:
            lines = f.readlines()

            for l in lines:
                parts = l.split(', ')
                page = int(parts[0])
                time = int(parts[1])
                if time > limit:
                    time = limit

                # our pages start at 1, but the list indices at zero, so always subtract 1:
                if len(responsetimes) > page-1:
                    responsetimes[page-1].append(time)
                else:
                    responsetimes.append([time])

    return responsetimes


# Loads the log.txt files into one big dictionary
def getClicks():
    clicks = {}
    for r in responses:
        s = str(r["session"])
        logfile = s+'/log.txt'

        with open(logfile) as f:
            lines = f.readlines()

            for l in lines:
                parts = l.split(', ')
                # init the sub-dictionary if we're at the first page:
                if parts[0] == '1':
                    clicks[s] = {}

                # init the sub-sub dict for the current page:
                clicks[s][parts[0]] = {}

                # and fill it
                clicks[s][parts[0]]["time"] = int(parts[1])
                clicks[s][parts[0]]["lon"] = float(parts[2])
                clicks[s][parts[0]]["lat"] = float(parts[3])

    # pprint.pprint(clicks)
    return clicks


def openGeoJSON(session, page):
    with open(str(r["session"])+"/"+str(page)+".json") as f:
        data = json.load(f)
        # pprint.pprint(data)
        return data


def getCoordsByValue(session, page, value):
    data = openGeoJSON(session, page)
    for feature in data['features']:
        # Careful here: high accuracy values actually mean high uncertainty. Don't ask me why I did it that way...
        if feature['properties']['accuracy'] == value:
            return feature['geometry']['coordinates']

    # return an empty array if no point with accuracy of 'value' is found, which should never happen
    print "No point found... this shouldn't happen!"
    return []

def getMostUncertain(session, page):
    return getCoordsByValue(session, page, 7)

def getLeastUncertain(session, page):
    return getCoordsByValue(session, page, 1)


def getClosest(session, page, clickpoint):

    print session
    print page
    print clickpoint

    data = openGeoJSON(session, page)

    # initialize the shortest distance with a very high value:
    shortest = 100000000.0
    u = 0

    for feature in data['features']:
        d = getDist(feature['geometry']['coordinates'], clickpoint)
        if d < shortest:
            print "Found a shorter distance: " + str(d) + "; Point: " + str(feature['geometry']['coordinates'])
            shortest = d
            u = feature['properties']['accuracy']
    print
    return u


responses = []
os.chdir(os.path.expanduser("~")+"/Dropbox/Code/UncertD3/evaluation/data/")

# download the CSV with the up-to-date interview responses to have a backup
response = urllib.urlopen("http://carsten.io/uncertainty/experiments/questionnaires.csv")

# download csv to string
text = response.read()

#fix formatting of csv:
text = text.replace(", ", ",").replace(",\n", "\n")

# save to local file as backup:
with open("questionnaires.csv", "w") as text_file:
    text_file.write(text)

# then read in this local csv file as dict
with open("questionnaires.csv", 'rb') as csvfile:
    # r = csv.reader(csvfile, delimiter=',', quotechar='|')
    rs = csv.DictReader(csvfile, delimiter=',')
    for r in rs:
        responses.append(r)

print "n = " + str(len(responses))

# next, go through all the sessions and check if we already have a copy of the data for that session;
# if not, download the data:
for r in responses:
    if not os.path.exists(str(r["session"])):
        print "Downloading new data for session " +str(r["session"])+ "..."
        os.makedirs(str(r["session"]))
        for i in range(1,12):
            path = str(r["session"])+"/"+str(i)+".json"
            urllib.urlretrieve ("http://carsten.io/uncertainty/experiments/"+path, path)
            path = str(r["session"])+"/log.txt"
            urllib.urlretrieve ("http://carsten.io/uncertainty/experiments/"+path, path)

# on to the actual analysis:
# first, some pie charts
matplotlib.style.use("fivethirtyeight")
ftecolors = ['#fc4f30', '#008fd5', '#e5ae38', '#6d904f', '#8b8b8b', '#810f7c']

# gender:

# gather the data
labels, counts = gatherPieData(responses, "gender")
total = sum(counts)

plt.pie(counts, labels=labels, colors=ftecolors, autopct=lambda(p): '{:.0f}'.format(p * total / 100), shadow=False, startangle=90)
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

colors = ['#008fd5', '#33bbff', '#005f8f', '#fc4322', '#B51D03', '#FB310E', '#DD2403', '#C92103', '#fc4f30', '#A11A02', '#F12704', '#8b8b8b']

for key, value in d.iteritems():

    labels, counts = gatherPieData(responses, key)
    total = sum(counts)

    plt.pie(counts, labels=labels, colors=colors, autopct=lambda(p): '{:.0f}'.format(p * total / 100), shadow=False, startangle=90)

    plt.axis('equal')
    plt.suptitle(value)
    plt.savefig("../plots/"+key+".pdf")


    plt.clf()


# age box plot:
ages = []
for r in responses:
    ages.append(int(r["age"]))

plt.boxplot(ages)
plt.suptitle("Age distribution")
plt.savefig("../plots/age.pdf")

plt.clf()


# make a box plot of the response times:
# plt.boxplot(getresponsetimes(responses), 0, '')
plt.boxplot(getresponsetimes(responses))
plt.suptitle("Response times")
plt.savefig("../plots/responsetimes.pdf")

plt.clf()

# Let's take a look at the GeoJSON files and click locations. First, load the click logs:
clicks = getClicks();

distances = []
clostests = []

# go through all sessions:
for session in clicks:
    s = clicks[session]
    for page in s:
        # the uneven pages ask for the MOST uncertain object,
        # the even pages for the LEAST uncertain object

        clickpoint = [s[page]['lon'], s[page]['lat']]
        page = int(page)

        if page % 2 == 0: # even
            # look for the least uncertain object in the corresponding geojson
            maxP = getLeastUncertain(session, page)
        else:  # not even
            # look for the most uncertain object in the corresponding geojson
            maxP = getMostUncertain(session, page)

        # and calculate the distance to the click
        d = getDist(maxP, clickpoint)

        # collect all distances in a list of lists by page
        # our pages start at 1, but the list indices at zero, so always subtract 1:
        if len(distances) > page-1:
            distances[page-1].append(d)
        else:
            distances.append([d])

        # collect all uncertainty values in a list of lists by page
        # look for the closest point to the click and check its uncertainty
        c = getClosest(session, page, clickpoint)
        if len(clostests) > page - 1:
            clostests[page-1].append(c)
        else:
            clostests.append([c])



# make a box plot of the distances:
plt.boxplot(distances)
plt.suptitle("Distances")
plt.savefig("../plots/distances.pdf")

plt.clf()


# and one of the uncertainty values of the closest points:
plt.boxplot(clostests)
plt.suptitle("Uncertainty of closest point")
plt.savefig("../plots/clostest.pdf")

plt.clf()



# iterate through all individual participant responses:
# for r in responses:
#     for i in range(1, 12):
#         try:
#             with open(str(r["session"])+"/"+str(i)+".json") as f:
#                 data = json.load(f)
#         except Exception as e:
#             print str(r["session"])+"/"+str(i)+".json"
#             print e

        # for feature in data['features']:
        #     print feature['properties']['accuracy']
        #     coords = feature['geometry']['coordinates']
            # print Point(coords[0],coords[1]).distance(Point(coords[0],coords[1]))
    # path = str(r["session"])+"/log.txt"
    # urllib.urlretrieve ("http://carsten.io/uncertainty/experiments/"+path, path)
