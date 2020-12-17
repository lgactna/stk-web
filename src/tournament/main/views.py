from django.shortcuts import render

from django.views import generic
from django.http import Http404
from django.db.models import Avg, F, Window
from django.db.models.functions import Rank

from main.models import Player, Team, Map, Mappool

# Create your views here.
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_players = Player.objects.all().count()

    y = Player.objects.annotate(
        rank=Window(
            expression=Avg('scores__score')
        )
    )

    '''
    tomorrow:

    Try doing an aggregate and then an annotation, in that order.
     
    The first is to establish the average for each player.
    player_avg = player.scores.all().aggregate(Avg('score'))
    It looks like this can be done using an annotation as well.

    Then we annotate the rank of that average using the things found here:
    https://stackoverflow.com/questions/55260238/django-orm-create-ranking-based-on-related-model-count
    https://docs.djangoproject.com/en/2.2/topics/db/aggregation/

    Maybe it's even possible to combine annotations, as in

    rank = Window(
        expression=Rank(),
        order_by=F('average_score').desc()
    )

    qs = Player.objects.annotate(average_score=Avg('scores__score')).annotate(rank=rank)
    then maybe we iterate over the queryset and assign???

    see https://stackoverflow.com/questions/3652736/django-update-queryset-with-annotation
    '''

    for player in y:
        print(player.rank)

    context = {
        'num_players': num_players,
        'y': y
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

def player_detail_view(request, pk):
    try:
        player = Player.objects.get(pk=pk)
    except Player.DoesNotExist:
        raise Http404('Player does not exist')

    player_avg = player.scores.all().aggregate(Avg('score'))

    return render(request, 'main/player_detail.html', context={'player': player, 'player_avg': player_avg, 'test': test})
