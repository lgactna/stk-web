from django.shortcuts import render

from django.views import generic
from django.http import Http404
from django.db.models import Avg, OuterRef, Subquery, F, Window
from django.db.models.functions import Rank, RowNumber

from main.models import Player, Team, Map, Mappool

# Create your views here.
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_players = Player.objects.all().count()

    Player.objects.update( 
        average_score=Subquery( 
            Player.objects.filter( 
                osu_id=OuterRef('osu_id') 
            ).annotate( 
                avg_score=Avg('scores__score') 
            ).values('avg_score')[:1] 
        ) 
    )
    '''
    s_rank = Window(
        expression=Rank(), 
        order_by=F('average_score').desc(),
        partition_by=[F('osu_id')]
    )
    '''
    qs = Subquery(Player.objects
    .filter(osu_id=OuterRef('osu_id'))
    .annotate(average=Avg('scores__score'))
    .order_by('-average')
    .annotate(rank = Window(expression=RowNumber()))
    .values('rank')[:1]
    )

    print(qs)

    
    Player.objects.update( 
        score_rank=qs 
    )
    
    #p = Player.objects.order_by('-average_score').annotate(rank=Window(expression=RowNumber()))
    #print(p.values('rank')[:1])
    
    '''
    for p in Player.objects.annotate():
        p.score_rank = None
        p.save()
    '''
    '''
    https://stackoverflow.com/questions/55260238/django-orm-create-ranking-based-on-related-model-count
    https://docs.djangoproject.com/en/2.2/topics/db/aggregation/
    https://stackoverflow.com/questions/3652736/django-update-queryset-with-annotation
    https://stackoverflow.com/questions/35781669/clean-way-to-use-postgresql-window-functions-in-django-orm
    '''

    context = {
        'num_players': num_players
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

def player_detail_view(request, pk):
    try:
        player = Player.objects.get(pk=pk)
    except Player.DoesNotExist:
        raise Http404('Player does not exist')

    player_avg = player.scores.all().aggregate(Avg('score'))

    return render(request, 'main/player_detail.html', context={'player': player, 'player_avg': player_avg})
