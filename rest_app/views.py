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


from rest_framework.pagination import LimitOffsetPagination

from functools import reduce


class SearchViewElk(APIView, LimitOffsetPagination):

    default_limit = 10
    serializer_class = MovieHayStackSerializer

    def get(self, request):

        # get the query params
        query = request.GET.get("q", None)
        highlight = request.GET.get("highlight", None)
        facets = request.GET.get("facets", None)

        # prepare a initial elk SearchQuerySet from Movie Model
        sqs = SearchQuerySet().models(Movie)

        if query:
            query_list = query.split(" ")  # split the query string
            qs_item = reduce(
                operator.and_, (Q(text__contains=item) for item in query_list)
            )  # filter by every item in query_list - ( using OR filter)
            sqs = sqs.filter(qs_item)

            if highlight:
                # if any value is passed to highlight then highlight the query
                sqs = sqs.highlight()

        if facets:
            sqs = self.filter_sqs_by_facets(sqs, facets)

        page = self.paginate_queryset(sqs, request, view=self)
        movie_serializer = self.serializer_class(
            page, many=True, context={"request": request}
        )
        facets = self.get_facet_fields(sqs)
        summary = self.prepare_summary(sqs)
        data = {"movies": movie_serializer.data, "facets": facets, "summary": summary}
        return Response(data, status=status.HTTP_200_OK)

    def filter_sqs_by_facets(self, sqs, facets):
        facet_list = facets.split(",")
        for facet in facet_list:
            facet_key, facet_value = facet.split(":")
            # narrow down the results by facet
            sqs = sqs.narrow(f"{facet_key}:{facet_value}")
        return sqs

    def get_facet_fields(self, sqs):
        # return all the possible facet fields from given SQS
        facet_fields = (
            sqs.facet("year")
            .facet("rating")
            .facet("global_ranking")
            .facet("length")
            .facet("revenue")
            .facet("country")
            .facet("genre")
        )
        return facet_fields.facet_counts()

    def prepare_summary(self, sqs):
        # return the summary of the search results
        summary = {
            "total": sqs.count(),
            "next_page": self.get_next_link(),
            "previous_page": self.get_previous_link(),
        }
        return summary