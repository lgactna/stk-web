from django.shortcuts import render

from django.views import generic

from main.models import Player, Team, Map, Mappool

# Create your views here.
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_players = Player.objects.all().count()

    context = {
        'num_players': num_players,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class PlayerDetailView(generic.DetailView):
    model = Player