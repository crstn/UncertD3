import urllib, os, csv

responses = []
folder = os.path.expanduser("~")+"/Dropbox/Code/UncertD3/evaluation/data/"
# download the CSV with the up-to-date interview responses to have a backup
response = urllib.urlopen("http://carsten.io/uncertainty/experiments/questionnaires.csv")

# download csv to string
text = response.read()

#fix formatting of csv:
text = text.replace(", ", ",").replace(",\n", "\n")

# save to local file as backup:
with open(folder+"questionnaires.csv", "w") as text_file:
    text_file.write(text)

# then read in this local csv file as dict
with open(folder+"questionnaires.csv", 'rb') as csvfile:
    # r = csv.reader(csvfile, delimiter=',', quotechar='|')
    rs = csv.DictReader(csvfile, delimiter=',')
    for r in rs:
        responses.append(r)

# next, go through all the sessions and check if we already have a copy of the data for that session:
for r in responses:
    if os.path.exists(folder+str(r["session"])):
        print "Data for session " +str(r["session"])+ " already downloaded."
    else:
        print "Downloading data for session " +str(r["session"])+ "..."
        os.makedirs(folder+str(r["session"]))
        for i in range(1,12):
            path = str(r["session"])+"/"+str(i)+".json"
            urllib.urlretrieve ("http://carsten.io/uncertainty/experiments/"+path, folder+path)
            path = str(r["session"])+"/log.txt"
            urllib.urlretrieve ("http://carsten.io/uncertainty/experiments/"+path, folder+path)
