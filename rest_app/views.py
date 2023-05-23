from django.shortcuts import get_object_or_404

from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import parser_classes
from rest_framework.decorators import api_view

from .serializers import MovieHayStackSerializer, MovieSerializer
from .models import Movie
from rest_framework.views import APIView
import operator

from django.db.models import Q

@api_view(["GET", "POST"])
@parser_classes([JSONParser, MultiPartParser])
def movie_get_post(request):
    """
    List all movie, or create a new movie.
    """
    if request.method == "GET":
        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True, context={'request': request})
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = MovieSerializer(data=request.data)

        if serializer.is_valid():
            # Create the Movie instance from the validated data
            movie_instance = serializer.save()

            # Explicitly save the new Movie instance to the database
            movie_instance.save()

            # Use the Movie instance in the response data
            return Response(
                {
                    "success": True,
                    "data": movie_instance.data,
                    "message": "Movie created successfully.",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@parser_classes([JSONParser])
def movie_pk(request, pk):
    """
    Retrieve, update or delete an Movie.
    """
    movie = get_object_or_404(Movie, pk=pk)

    if request.method == "GET":
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = MovieSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "data": serializer.data,
                    "message": "Movie edited successfully.",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        movie.delete()
        return Response(
            {"success": True, "message": "Movie deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


#########################################Haystack Work Here#########################################

from .search_indexes import MovieIndex
from haystack.query import SearchQuerySet

from urllib.parse import unquote


from functools import reduce
from drf_haystack.viewsets import HaystackViewSet

class SearchViewElk(HaystackViewSet):
    index_models = [Movie]
    serializer_class = MovieHayStackSerializer

    def filter_queryset(self, queryset):
        params = self.request.query_params

        # Iterate over the query parameters and apply filters
        for key, value in params.items():
            # Skip 'format' and 'callback' parameters, which are not filters
            if key in ['format', 'callback']:
                continue

            # Apply filters based on the field name and value
            if '__' in key:
                field_name, filter_type = key.split('__')
                lookup_expr = f'{field_name}__{filter_type}'
                queryset = queryset.filter(**{lookup_expr: value})
            else:
                queryset = queryset.filter(**{key: value})

        return queryset