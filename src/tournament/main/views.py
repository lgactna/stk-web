from django.shortcuts import render

from django.views import generic
from django.http import Http404

from main.models import Player, Team, Map, Mappool
from main.ranking import update_rankings

#this can go to a celery task or other like services.py


# Create your views here.
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_players = Player.objects.all().count()

    #obviously move this elsewhere later but see if works for now
    update_rankings()

    context = {
        'num_players': num_players,
        'js_thing': ['df', 'df']
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

def player_detail_view(request, pk):
    try:
        player = Player.objects.get(pk=pk)
    except Player.DoesNotExist:
        raise Http404('Player does not exist')

    return render(request, 'main/player_detail.html', context={'player': player})
