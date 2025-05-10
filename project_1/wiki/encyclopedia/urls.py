from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),

    path("random/", views.random, name="random"),

    path("create/<str:edit>", views.create, name="create"),

    path("search/", views.search, name="search"),

    path("edit/<str:title>/", views.edit, name="edit"),

    path("delete/<str:title>/", views.delete, name="delete"),

    path("wiki/<str:title>/", views.data, name="data")
]
