import argparse
import sys
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import six
import pandas as pd
from flask import Flask, request, jsonify
import pymysql
import phonetics
import os
# importing json key file

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="auth_key.json"
data = []
connection = pymysql.connect("db4free.net","gunjanrl","gunj@nrl","id4165564_olcade")
cursor = connection.cursor()

# [START def_entities_text]
def entities_text(text):
	global data
    """Detects entities in the text."""
    client = language.LanguageServiceClient()

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    # Instantiates a plain text document.
    # [START migration_analyze_entities]
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
        data.append(entity.name)
        #print('=' * 20)
        #print(u'{:<16}: {}'.format('name', entity.name))
        
    return entities

def databaseTI():
	global data 
	
	find_query = 'SELECT `description`,`count` FROM `newcourses`'
	cursor.execute(find_query)
	text = []
	text.append(cursor.fetchall())
	print(text[0][0][0])


	count = 1
	for collection in text[0]:
	    print(collection[1])
	    tags_final=[]
	    tags = entities_text(collection[0])
	    for tag in tags: tags_final.append(tag.name)
	    tags_final = set(tags_final)
	    find_query = 'SELECT `courseid` FROM `newcourses` WHERE count = '+str(collection[1])
	    cursor.execute(find_query)
	    result = cursor.fetchall()
	    print(result)
	    course_id = result[0][0]
	    #print(description[0])
	    #print(course_id)
	    for tag in tags_final:
	        #print(course_id + ' ' + tag)
	        insert_query = 'INSERT INTO `tags`(`course_id`, `tag`, `tagmp`) VALUES ('+course_id+',"'+ tag +'","'+ phonetics.dmetaphone(tag)[0] +'")'
	        cursor.execute(insert_query)
	print("->",data)
	df=pd.DataFrame(data)
	cursor.close()
	connection.commit()



	print("-<> ",phonetics.dmetaphone('blockchain'))
	return True

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def index():

    req_data = request.get_json()
    # cmt = req_data["ct"] #set from fe
    fin = databaseTI()
    resp = {
    "stat":fin
    }
    return jsonify(resp)


if __name__=="__main__":
    # app.run() #debug = True
    app.debug = True
    port = int(os.environ.get("PORT",5000))
    app.run(host='0.0.0.0',port = port)