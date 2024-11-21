from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from listings_app.models.search_query import SearchQuery
from listings_app.serializers.serializers import SearchQuerySerializer
from rest_framework import generics, filters

class SearchQueryListView(ListAPIView):
    serializer_class = SearchQuerySerializer
    permissions = [IsAuthenticated]


    def get_queryset(self):
        return SearchQuery.objects.filter(owner=self.request.user)
