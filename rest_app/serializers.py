# 3rd party imports
from drf_haystack.serializers import HaystackSerializer

# local imports
from .search_indexes import MovieIndex

from rest_framework import serializers

from .models import Movie

class MovieSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "description",
            "year",
            "rating",
            "global_ranking",
            "length",
            "revenue",
            "genre",
            "country",
            "director",
            
        ]
class MovieHayStackSerializer(HaystackSerializer):
    class Meta:
        # The `index_classes` attribute is a list of which search indexes
        # we want to include in the search.
        index_classes = [MovieIndex]

        # The `fields` contains all the fields we want to include.
        # NOTE: Make sure you don't confuse these with model attributes. These
        # fields belong to the search index!
        fields = [
            "title",
            "description",
            "year",
            "rating",
            "global_ranking",
            "length",
            "revenue",
            "genre",
            "country",
            "director",
            "autocomplete"
        ]
        ignore_fields = ["autocomplete"]
        field_aliases = {
            "q": "autocomplete"
        }
