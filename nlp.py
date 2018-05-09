from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import six
import csv
import re

def entities_text(text):
    """Detects entities in the text."""
    client = language.LanguageServiceClient()

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    # Instantiates a plain text document.
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    # Detects entities in the document. You can also analyze HTML with:
    #   document.type == enums.Document.Type.HTML
    entities = client.analyze_entities(document).entities

    # entity types from enums.Entity.Type
    entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
                   'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')

    for entity in entities:
        print('=' * 20)
        print(u'{:<16}: {}'.format('name', entity.name))
        print(u'{:<16}: {}'.format('type', entity_type[entity.type]))
        print(u'{:<16}: {}'.format('metadata', entity.metadata))
        print(u'{:<16}: {}'.format('salience', entity.salience))
        print(u'{:<16}: {}'.format('wikipedia_url',
              entity.metadata.get('wikipedia_url', '-')))

def classify_text(text):
    """Classifies content categories of the provided text."""
    client = language.LanguageServiceClient()

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    document = types.Document(
        content=text.encode('utf-8'),
        type=enums.Document.Type.PLAIN_TEXT)

    categories = client.classify_text(document).categories

    for category in categories:
        print(u'=' * 20)
        print(u'{:<16}: {}'.format('name', category.name))
        print(u'{:<16}: {}'.format('confidence', category.confidence))

# Instantiates a client
client = language.LanguageServiceClient()

model = []
category = []
product = []

with open('results-20171113-113815.csv', 'rb') as csvfile:
	rows = csv.reader(csvfile, delimiter=',', quotechar='\'')

	# The text to analyze
	for line in rows:
#		if line[0] in ['samsung', 'iphone']:
		if line[0] in ['samsung']:
			text = line[2]
			if re.search('^[(samsung)(samsung galaxy)]?[ajs(note)].*[3-8]$', text):
#				print text
				model.append([text, text])
			if re.search('(case|glass|cover)$', text):
#				print text
				category.append([text, text])
			# classify_text(text)
#			entities_text(text)
		elif line[0] in ['lg', 'iphone']:
			text = line[2]
			if re.search('(protector|cable|case|glass|cover|spigen|casing|charger)', text):
				print "\t\t\t: " + text
				category.append([text, text])
			else:
				print text

#	print category

with open('model.csv', 'wb') as csvfile:
#	writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
	for line in model:
		writer.writerow(line)

with open('category.csv', 'wb') as csvfile:
	writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
	for line in category:
		writer.writerow(line)


