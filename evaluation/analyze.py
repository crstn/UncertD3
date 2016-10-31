import urllib, os, csv, matplotlib
import matplotlib.pyplot as plt

# some helper functions:
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

    return labels, counts

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
colors = ['#008fd5', '#fc4f30', '#e5ae38', '#6d904f', '#8b8b8b', '#810f7c']

# gender:

# gather the data
labels, counts = gatherPieData(responses, "gender")
total = sum(counts)

plt.pie(counts, labels=labels, colors=colors, autopct=lambda(p): '{:.0f}'.format(p * total / 100), shadow=False, startangle=90, explode = (0.05, 0))
# Set aspect ratio to be equal so that pie is drawn as a circle.
plt.axis('equal')
plt.suptitle('Gender breakdown')
plt.savefig("../plots/gender.pdf")



plt.clf()

# best and worst viz types

for t in ["bestmost", "bestleast", "worstmost", "worstleast"]:

    labels, counts = gatherPieData(responses, t)
    total = sum(counts)

    plt.pie(counts, labels=labels, colors=colors, autopct=lambda(p): '{:.0f}'.format(p * total / 100), shadow=False, startangle=90)

    plt.axis('equal')
    # plt.suptitle('Best visualization to identify most uncertain object')
    plt.savefig("../plots/"+t+".pdf")


plt.clf()
