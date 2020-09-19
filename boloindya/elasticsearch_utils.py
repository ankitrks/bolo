
import requests
import boto3
import json
#from requests_aws4auth import AWS4Auth 
#from elasticsearch import Elasticsearch, RequestsHttpConnection, helpers 
from django.conf import settings

service = 'es'
headers = {'Content-Type': 'application/json'}


class ElasticSearch:

    def __init__(self, *args, **kwargs):
        # credentials = boto3.Session().get_credentials()
        # self.auth = AWS4Auth(credentials.access_key, credentials.secret_key, settings.ES_7_CONFIG.get('region'), service)    
        self.auth = (settings.ES_7_CONFIG.get('username'), settings.ES_7_CONFIG.get('password'))


    def search(self, index_name, query):
        url = 'https://' + settings.ES_7_CONFIG.get('host') + '/%s/_search'%index_name
        # print("Query", json.dumps(query, indent=3))
        response = requests.get(url, headers=headers, json=query, auth=self.auth)

        if response.ok:
            return json.loads(response.text)
        else:
            raise Exception(response.text)

    def get_es_connection(self):
        return Elasticsearch( 
                hosts=[{'host': settings.ES_7_CONFIG.get('host'), 'port': 443}], 
                http_auth=self.auth, 
                use_ssl=True, 
                verify_certs=True, 
                connection_class=RequestsHttpConnection 
            )

    def search2(self, index_name, query):
        return self.get_es_connection().search(index=index_name, body=query)
