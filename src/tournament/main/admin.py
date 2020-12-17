from django.contrib import admin

from .models import Player, Role, Team, Score, Map, Mappool, Match, Stage

# Register your models here.

#admin.site.register(Player)
admin.site.register(Role)
#admin.site.register(Team)
#admin.site.register(Score)
#admin.site.register(Map)
#admin.site.register(Mappool)
#admin.site.register(Match)
#admin.site.register(Stage)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('osu_id', 'osu_name', 'team')
    list_filter = ('team', 'roles')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'get_players')

    #note: this is likely creating a query on each
    #there is almost certainly a better way
    #https://stackoverflow.com/questions/38827608/get-list-display-in-django-admin-to-display-the-many-end-of-a-many-to-one-rela?
    def get_players(self, obj):
        players_str = ""
        for player in obj.players.all():
            players_str += player.osu_name+", "
        players_str = players_str[:-2] #clear last commas
        return players_str
    get_players.short_description = 'Players'  #Renames column head

@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'mappool', 'pool_id')
    list_filter = ('mappool', 'map_type')
    fields = [
        ('diff_id', 'set_id'), 
        ('artist', 'title', 'diff_name'),
        'creator',
        ('mappool', 'pool_id', 'map_type'), 
        ('star_rating', 'duration'),
        ('cs', 'ar', 'od', 'hp'),
        ('star_rating_alt', 'duration_alt'),
        ('cs_alt', 'ar_alt', 'od_alt', 'hp_alt'),]

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('return_str', 'return_pool', 'return_id', 'return_mp')
    list_filter = ('map__mappool', 'map__map_type')
    
    #unfortunately...
    #https://code.djangoproject.com/ticket/5863
    #https://stackoverflow.com/questions/3409970/django-admin-how-to-display-fields-from-two-different-models-in-same-view
    #there exists no way to represent these in list_display without a function
    #however, they work perfectly fine in list_filter which is why they're used there
    def return_str(self, obj):
        return obj.player.osu_name + " | " + obj.map.artist + " - " + obj.map.title
    return_str.short_description = 'Player - Map'

    def return_pool(self, obj):
        return obj.map.mappool
    return_pool.short_description = 'Pool'

    def return_id(self, obj):
        return obj.map.pool_id
    return_id.short_description = 'Pool ID'

    def return_mp(self, obj):
        return obj.match.mp_id
    return_mp.short_description = 'Match MP'

@admin.register(Mappool)
class MappoolAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'display_order')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('match_id', 'team_1', 'score_1', 'score_2', 'team_2', 'utc_time', 'referee')
    fields = [
        ('team_1', 'score_1', 'score_2', 'team_2'), 
        ('match_id', 'utc_time'),
        ('stage', 'mappool'),
        ('referee', 'streamer', 'commentators'), 
        'mp_id',
        'vod_link',]

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date_display')