import os
import django

# set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest_project.settings')

# initialize Django
django.setup()

# import models and use them
from rest_app.models import Product
from rest_app.documents import ProductDocument

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q

client = Elasticsearch()

def get_products_with_high_prices():
    s = Search(using=client, index="product")
    s = s.filter("range", price={"gt": 10000})
    response = s.execute()
    return response.to_dict()["hits"]["hits"]

print(get_products_with_high_prices())
