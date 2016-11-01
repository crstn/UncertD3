import urllib, os, csv, matplotlib, json
import matplotlib.pyplot as plt
from shapely.geometry import Point

# some helper functions:

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


def getresponsetimes(responses):

    responsetimes = []

    for r in responses:
        logfile = str(r["session"])+'/log.txt'
        with open(logfile) as f:
            lines = f.readlines()

            for l in lines:
                parts = l.split(', ')
                page = int(parts[0])
                time = int(parts[1])

                # our pages start at 1, but the list indices at zero, so always subtract 1:
                if len(responsetimes) > page-1:
                    responsetimes[page-1].append(time)
                else:
                    responsetimes.append([time])

    return responsetimes




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
ftecolors = ['#008fd5', '#fc4f30', '#e5ae38', '#6d904f', '#8b8b8b', '#810f7c']

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
plt.boxplot(getresponsetimes(responses), 0, '')
plt.suptitle("Response times")
plt.savefig("../plots/responsetimes.pdf")

plt.clf()

# let's take a look at the GeoJSON files and click locations:
# iterate through all individual participant responses:
for r in responses:
    for i in range(1, 12):
        with open(str(r["session"])+"/"+str(i)+".json") as f:
            data = json.load(f)

        # for feature in data['features']:
        #     print feature['properties']['accuracy']
        #     coords = feature['geometry']['coordinates']
            # print Point(coords[0],coords[1]).distance(Point(coords[0],coords[1]))
    # path = str(r["session"])+"/log.txt"
    # urllib.urlretrieve ("http://carsten.io/uncertainty/experiments/"+path, path)
