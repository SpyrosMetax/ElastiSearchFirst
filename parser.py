import os
from elasticsearch import Elasticsearch
import bibtexparser

#Εδω μπορώ να αλλάξω το αρχείο από το οποίο παίρνουμε τις πληροφορίες απλά και ωραία
BIB_FILE = "DIT-UoP publications.bib"

INDEX_NAME = "pulp"

# πληροφορίες σύνδεσης,
#ΣΗΜΕΙΩΣΗ, το cert πρέπει να βρίσκεται στην ίδιο φάκελο με τον κώδικα αυτόν
#Αλλιώς να βάλω μονοπάτι στο ca_certs = "/path_to/http_ca.crt"
ELASTIC_PSW = input("Enter Elasticsearch password: ")

client = Elasticsearch(
    "https://localhost:9200",
    ca_certs="http_ca.crt",
    basic_auth=("elastic",ELASTIC_PSW),
    request_timeout=60
)



with open(BIB_FILE, encoding="utf-8") as file:
    library = bibtexparser.load(file)

print(".")

#print(df)

#Αν στην elastic το έχουμε γεμίσει, τότε το διαγράφουμε για να φτιάξουμε καινούριο 
if client.indices.exists(index=INDEX_NAME):
    print("deleting existing index")
    client.indices.delete(index=INDEX_NAME)

print("..")

mapping = {
    "settings":{
        "analysis": {
            "analyzer": {
                "my_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "stop",
                        "porter_stem"
                    ]
                }
            }
        }
    },
    "mappings":{
        "properties":{
            "author":{
                "type": "text",
                "analyzer": "my_analyzer"#αποκλοίει stop words, case folding, stemming
            },
            "title":{
                "type": "text",
                "analyzer": "my_analyzer"
            },
            "booktitle":{
                "type": "text",
                "analyzer": "my_analyzer"
            },
            "journal":{
                "type": "text",
                "analyzer": "my_analyzer"
            },
            "year": {
                "type": "keyword"
            },
            "doi": {
                "type": "keyword"
            },
            "biburl": {
                "type": "keyword"
            }
        }
    }
}

client.indices.create(index=INDEX_NAME,body=mapping)

print("Parsing ")
print("...")

for index,entry in enumerate(library.entries):
    document_data = {
                "author": entry.get("author",""),
                "title": entry.get("title",""),
                "booktitle": entry.get("booktitle",""),
                "journal": entry.get("journal",""),
                "year": entry.get("year",""),
                "doi": entry.get("doi",""),
                "biburl": entry.get("biburl","")
    }

    client.index(
                index=INDEX_NAME,
                id=str(index),
                document=document_data,
    )

# printing the client info
print("Successful")
