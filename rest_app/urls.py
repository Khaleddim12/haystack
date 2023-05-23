from django.urls import path
from .views import movie_get_post, movie_pk, SearchViewElk
from rest_framework import routers



urlpatterns = [
    path('', movie_get_post),
    path('<int:pk>', movie_pk),
    path('search/', SearchViewElk.as_view({'get': 'list'})),
]

