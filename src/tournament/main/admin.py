from django.contrib import admin

from .models import Player, Role, Team, Score, Map, Mappool, Match, Stage

# Register your models here.

admin.site.register(Player)
admin.site.register(Role)
admin.site.register(Team)
admin.site.register(Score)
admin.site.register(Map)
admin.site.register(Mappool)
admin.site.register(Match)
admin.site.register(Stage)
