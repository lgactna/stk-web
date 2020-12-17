from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('player/<int:pk>', views.player_detail_view, name='player-detail'),
]
