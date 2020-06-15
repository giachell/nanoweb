from django.urls import path
from . import views

app_name="Nanoweb"

# NanowebMainApp URL Configuration


urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('stats/', views.stats, name='stats'),
    path('stats/json/', views.stats_json, name='stats_json'),
    path('query/<queryText>/', views.query, name='query'),
    path('nanopubs/<query>/', views.nanopubs, name='nanopubs'),
    path('querysuggestions/<queryText>/', views.querysuggestions, name='querysuggestion'),
    path('node_linked_elements/<node>/', views.node_linked_elements, name='node_linked_elements'),
    path('entity_properties/<entity>/', views.entity_properties, name='entity_properties'),
    path('nanopub_related_to/<source>/<target>', views.nanopub_related_to, name='nanopub_related_to'),
    path('queries', views.queries, name='queries'),
    path('results/<queryText>/', views.results, name='results'),
    path('search', views.search, name='search'),
    path('nanopubinfo/<nanopubIdentifier>/', views.nanopubinfo, name='nanopubinfo'),
    path('nanopub/<nanopubIdentifier>/', views.nanopub, name='nanopub'),
]
