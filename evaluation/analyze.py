import urllib, os, csv


questionnaires = os.path.expanduser("~")+"/Dropbox/Code/UncertD3/evaluation/data/questionnaires.csv"
# download the CSV with the up-to-date interview responses to have a backup
# urllib.urlretrieve ("http://carsten.io/uncertainty/experiments/questionnaires.csv", questionnaires)
response = urllib.urlopen("http://carsten.io/uncertainty/experiments/questionnaires.csv")

# download csv to string
text = response.read()

#fix formatting of csv:
text = text.replace(", ", ",").replace(",\n", "\n")

# save to local file as backup:
with open(questionnaires, "w") as text_file:
    text_file.write(text)

# then read in this local csv file as dict
with open(questionnaires, 'rb') as csvfile:
    # r = csv.reader(csvfile, delimiter=',', quotechar='|')
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        print row['session']
