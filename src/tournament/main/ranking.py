from django.db.models import Avg, OuterRef, Subquery, F, Window
from django.db.models.functions import Rank, RowNumber

from main.models import Player, Team, Map, Mappool
    
def update_player_rankings():
    #generate averages
    Player.objects.update( 
        average_score=Subquery( 
            Player.objects.filter( 
                osu_id=OuterRef('osu_id') 
            ).annotate( 
                avg_score=Avg('scores__score') 
            ).values('avg_score')[:1] 
        ),
        average_acc=Subquery( 
            Player.objects.filter( 
                osu_id=OuterRef('osu_id') 
            ).annotate( 
                avg_acc=Avg('scores__accuracy') 
            ).values('avg_acc')[:1] 
        ),
        average_contrib=Subquery( 
            Player.objects.filter( 
                osu_id=OuterRef('osu_id') 
            ).annotate( 
                avg_contrib=Avg('scores__contrib') 
            ).values('avg_contrib')[:1] 
        ) 
    )

    #update ranks
    rank_score = Window(expression=Rank(), order_by=F('average_score').desc())
    rank_acc = Window(expression=Rank(), order_by=F('average_acc').desc())
    rank_contrib = Window(expression=Rank(), order_by=F('average_contrib').desc())
    d = Player.objects.filter().annotate(rank_s=rank_score, rank_a=rank_acc, rank_c=rank_contrib)
    for p in d:
        Player.objects.filter(osu_id=p.osu_id).update(score_rank=p.rank_s, acc_rank=p.rank_a, contrib_rank=p.rank_c)


    '''i suspect the reason as to why this doesn't work is because windows
    will be relative to the subqueries; it works above because the aggregation
    avg(whatever) can be calculated without knowledge of the other rows
    
    on the other hand, this completely falls apart because when the Subquery
    is executed, the scope of Window() will be for each player alone, and so each
    player (relative to themselvses) is rank #1, and that's what shows up
    i have no idea how to isolate the Window function or give it the information
    it needs'''
    '''
    rank_w = Window(expression=Rank(), order_by=F('average_score').desc())
    d = Player.objects.filter().annotate(rank=rank_w)

    print(d)
    print(d.values())
    
    Player.objects.update(contrib_rank=Subquery( 
            Player.objects.filter( 
                osu_id=OuterRef('osu_id') 
            ).annotate( 
                rank=rank_w
            ).values('rank')[:1] 
        ) ) 
    '''
    #supposedly it's possible that it's because RowNumber(), Rank() etc don't work
    #properly on SQLite, but do work properly on Postgres

    
    '''
    for index, p in enumerate(Player.objects.order_by('-average_score')):
        p.score_rank = index+1

    for index, p in enumerate(Player.objects.order_by('-average_acc')):
        p.acc_rank = index+1

    for index, p in enumerate(Player.objects.order_by('-average_contrib')):
        p.contrib_rank = index+1
    '''
    '''
    some links:
    https://stackoverflow.com/questions/55260238/django-orm-create-ranking-based-on-related-model-count
    https://docs.djangoproject.com/en/2.2/topics/db/aggregation/
    https://stackoverflow.com/questions/3652736/django-update-queryset-with-annotation
    https://stackoverflow.com/questions/35781669/clean-way-to-use-postgresql-window-functions-in-django-orm
    '''

def update_team_rankings():
    pass

def update_player_osu_data():
    pass

def initialize_player_osu_data():
    pass