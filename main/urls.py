
from django.contrib import admin
from django.urls import path, include
from .views import index, search, classifier

urlpatterns = [
    path('', index),
    path('search/', search),
    path('classifier/', classifier)

]
