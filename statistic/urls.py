from django.urls import path
from statistic import views as statisticsViews

urlpatterns = [
    path('', statisticsViews.visualizeStatistics, name="statistics"),
]
