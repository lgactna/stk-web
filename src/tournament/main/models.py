from django.db import models

#consider using ids (numbers) instead of full text names
from django.urls import reverse
from django.db.models.functions import Lower

# Create your models here.
class Player(models.Model):
    """Model representing a player.
    
    Relationships to others (a player can have many of these):
    - Role (related_name = "roles")
    - Score (related_name = "scores")
    - Matches (related_name = "matches" OR "reffed_matches" OR "commentated_matches" OR "streamed_matches") """
    osu_id = models.CharField(
        primary_key=True,
        max_length=10, 
        help_text="The player's osu! ID.", 
        verbose_name="osu! ID")
    osu_name = models.CharField(
        max_length=30,
        help_text="The player's osu! username.", 
        verbose_name="osu! username")
    
    roles = models.ManyToManyField("Role", related_name="players", blank=True)
    is_staff = models.BooleanField(
        help_text="Whether this user is a staff member or not.",
        verbose_name="Player is staff?")
    #in the future, we might make connections to a discord bot
    #but for now, we only store username#discriminator
    discord_name = models.CharField(max_length=100, help_text="The player's Discord tag (with discriminator).")

    #if a team is deleted, then this field is nulled
    #on a team instance, you would call team.players.all()
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, related_name='players')

    #before scores exist, we sort by username on tables and refs
    class Meta:
        ordering = [Lower('osu_name')]

    def get_absolute_url(self):
        """Returns the url for this player."""
        return reverse('player-detail', args=[str(self.osu_id)])

    def __str__(self):
        """String for representing the Model object.
        
        Returns their osu! username."""
        return self.osu_name

class Role(models.Model):
    """Model representing a role. 
    
    While these models have an "staff_role" (bool) field, this doesn't automatically
    change the status of player.is_staff."""
    role_name = models.CharField(
        primary_key=True, #mandatory uniqueness
        max_length=30,
    )
    role_color = models.CharField(
        max_length=9,
        help_text="RGBA hex (as #RRGGBBAA), webpage-compatible."
    )
    is_staff = models.BooleanField(
        help_text="Is this role staff-related? (has no effect on Player.is_staff)"
    )
    
    def __str__(self):
        """String for representing the Model object.
        
        Returns the role's name."""
        return self.role_name

class Team(models.Model):
    """Model representing a team.
    
    Relationships to others (a team can have many of these):
    - Player (related_name = "players")
    - Match (related_name = "matches_1" AND "matches_2") (not sure how to join, but just query both)
    """
    team_name = models.CharField(max_length=100)

    #before scores exist, we sort by team name on tables and refs
    class Meta:
        ordering = ['team_name']

    def __str__(self):
        """String for representing the Model object.
        
        Returns the team name."""
        return self.team_name
    
    def get_absolute_url(self):
        """Returns the url of this individual team."""
        return reverse('mappool-detail', args=[str(self.team_name)])

class Score(models.Model):
    """Model representing a score."""
    #metadata
    #formally speaking, players should never be deleted
    #but if a player is deleted, we can reasonably assume the intent is not for them
    #to keep influencing tournament statistics; same with a team or match
    #so cascade deletes this
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='scores')
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='scores')
    match = models.ForeignKey('Match', on_delete=models.CASCADE, related_name='scores')
    match_index = models.IntegerField(help_text="The index of this score relative to the match, zero-indexed.")
    #maps should normally not be deleted; direct deletion of a map after scores have been added is not allowed
    #if a map is replaced halfway through a weekend's matches, then the mappool ID should be unique to both
    #the deleted and existing maps of that mod (if NM1-NM6 exist and NM2 is thrown out, the replacing map should be NM7)
    #however, if an entire mappool is deleted (where Maps have a CASCADE rule, this is fine to delete)
    map = models.ForeignKey('Map', on_delete=models.RESTRICT, related_name='scores')

    score = models.IntegerField(help_text="The actual score value.")
    combo = models.IntegerField()
    accuracy = models.DecimalField(max_digits=6, decimal_places=3) # ###.#######
    team_total = models.IntegerField(
        help_text="The sum of this player's score and their teammates' scores for this map on that match.")
    contrib = models.DecimalField(max_digits=6, decimal_places=3)
    count_300 = models.IntegerField(verbose_name="300s")
    count_100 = models.IntegerField(verbose_name="100s")
    count_50 = models.IntegerField(verbose_name="50s")
    count_miss = models.IntegerField(verbose_name="Misses")
    
    class Meta:
        ordering = ['score', 'accuracy']

    def __str__(self):
        """String representation of a score.
        
        osugame style, no idea why you'd need this"""
        full = (f'{self.player.osu_name} | {self.map} ({self.map.creator} | '
                f'{self.map.star_rating}*) {self.accuracy} {self.combo}/{self.map.max_combo}')
        return full

class Map(models.Model):
    """Model representing a single map.
    
    More accurately, a single diff of a map in a mappool.
    
    A map can have many of these:
    - Score (related_name = "scores")
    
    You should enter alt_meta values (CS/AR/OD...) *after* applying the mod.
    This means if the drain time goes down due to DT, use alt_duration. The standard
    meta fields are *without* mod changes."""
    diff_id = models.CharField(
        primary_key=True, 
        max_length=15,
        help_text="The difficulty ID for this map, as in osu.ppy.sh/b/<id>",
        verbose_name="Difficulty ID")
    set_id = models.CharField(
        max_length=15,
        help_text="The set ID for this map, as in osu.ppy.sh/s/<id>",
        verbose_name="Beatmap Set ID")

    mappool = models.ForeignKey("Mappool", on_delete=models.CASCADE, related_name='maps')
    
    pool_id = models.CharField(
        max_length=5, #i hope you don't have anything more than NM999
        help_text="The mod pool+numerical ID of this map, as in NM1, DT2, etc."
    )

    #as of now, only the following types are supported
    #in the future, types can be delegated to a separate model with its
    #own color, name, shorthand name, css class, etc
    MAP_TYPES = (
        ('NM', "Nomod"),
        ('HD', "Hidden"),
        ('HR', "HardRock"),
        ('DT', "DoubleTime"),
        ('FM', "FreeMod"),
        ('TB', "Tiebreaker")
    )

    map_type = models.CharField(
        max_length=2,
        choices=MAP_TYPES,
        help_text='The mod this pool belongs in (NM, HR, etc.) TB is a separate "mod".'
    )

    #other map metadata
    artist = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    diff_name = models.CharField(max_length=100)
    creator = models.CharField(max_length=100)
    
    star_rating = models.DecimalField(max_digits=6, decimal_places=3)
    cs = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        verbose_name="CS",
        help_text="The map's circle size.")
    ar = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        verbose_name="AR",
        help_text="The map's approach rate.")
    od = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        verbose_name="OD",
        help_text="The map's overall difficulty.")
    hp = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        verbose_name="HP",
        help_text="The map's HP drain.")
    duration = models.IntegerField(
        verbose_name="Drain time",
        help_text = "Map's drain time in seconds."
    )

    #Alt, optional. Use if you need post-mod values to be shown.
    cs_alt = models.DecimalField(
        max_digits=5, 
        decimal_places=3,
        blank=True,
        null=True,
        verbose_name="Post-mod CS",
        help_text="The map's circle size, after applying mods.")
    ar_alt = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        blank=True,
        null=True,
        verbose_name="Post-mod AR",
        help_text="The map's approach rate, after applying mods.")
    od_alt = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        blank=True,
        null=True,
        verbose_name="Post-mod OD",
        help_text="The map's overall difficulty, after applying mods.")
    hp_alt = models.DecimalField(
        max_digits=5, 
        decimal_places=3,
        blank=True,
        null=True,
        verbose_name="Post-mod HP",
        help_text="The map's HP drain, after applying mods.")
    duration_alt = models.IntegerField(
        verbose_name="Post-mod drain time",
        help_text = "Map's drain time in seconds.",
        blank=True,
        null=True
    )

    def __str__(self):
        """String representation of a map.
        
        Returns `Artist - Title [Difficulty] (Mapper).`"""
        return f"{self.artist} - {self.title} [{self.diff_name}] ({self.creator})"

    def get_absolute_url(self):
        """Returns the url of this individual map."""
        return reverse('map-detail', args=[str(self.diff_id)])

    def long_name(self):
        """Longer string representation of a map.
        
        Intended for use with tooltips.
        Returns `Mappool stage/name, pool ID: Artist - Title [Difficulty] (set creator).`"""
        return f"{self.pool}, {self.pool_id}: {self.artist} - {self.title} [{self.diff_name}] ({self.creator})"

class Mappool(models.Model):
    '''Model representing a mappool.
    
    A mappool can have many of these:
    - Map (related_name = "maps")
    - Match (related_name = "matches")'''

    display_order = models.IntegerField(
        help_text="What index this pool is, unique. Pools are ordered highest first.", 
        primary_key=True)
    mappool_name = models.CharField(
        max_length=100,
        help_text="The full name of this mappool (as in Grand Finals).")
    short_name = models.CharField(
        max_length=10,
        help_text="The shorthand name for this mappool (as in SF, Ro32, etc.)")
    display_color = models.CharField(
        max_length=9,
        help_text="RGBA hex (as #RRGGBBAA), webpage-compatible."
    )

    class Meta:
        ordering = ['-display_order']

    def get_absolute_url(self):
        """Returns the url of this individual mappool."""
        return reverse('mappool-detail', args=[str(self.short_name)])

    def __str__(self):
        """String for representing the Model object.
        
        Returns the mappool name."""
        return self.mappool_name

class Match(models.Model):
    '''Model representing a match.
    
    Has:
    - ForeignKey relationship with two teams (one ForeignKey each)
    - ForeignKey relationship with one player, serving as the referee
    - ForeignKey relationship with one player, serving as the streamer
    - ManyToMany relationship with other players, serving as the commentators
    - ForeignKey relationsip with one mappool
    - ForeignKey relationship with one stage

    A match can have many of these:
    - Score (related_name = "scores")'''
    
    #matches shouldn't die if a team is deleted, so this is nullable
    #also, related_names are unique columns in a db and so have to be different. we'll just query for both and join when needed.
    team_1 = models.ForeignKey("Team", related_name='matches_1', on_delete=models.SET_NULL, null=True)
    team_2 = models.ForeignKey("Team", related_name='matches_2', on_delete=models.SET_NULL, null=True)
    score_1 = models.IntegerField(verbose_name='Team 1 Score', blank=True, null=True)
    score_2 = models.IntegerField(verbose_name='Team 2 Score', blank=True, null=True)
    utc_time = models.DateTimeField(verbose_name="UTC Time", blank=True, null=True)
    referee = models.ForeignKey("Player", related_name="reffed_matches", on_delete=models.SET_NULL, null=True, blank=True)
    streamer = models.ForeignKey("Player", related_name="streamed_matches", on_delete=models.SET_NULL, null=True, blank=True)
    commentators = models.ManyToManyField("Player", related_name="commentated_matches", blank=True)
    mappool = models.ForeignKey("Mappool", related_name='matches', on_delete=models.SET_NULL, null=True, blank=True)
    stage = models.ForeignKey("Stage", related_name='matches', on_delete=models.SET_NULL, null=True, blank=True)

    match_id = models.CharField(
        max_length=5,
        help_text="The internal match ID of the tournament (usually A1, B1, C2 for GS, 1-infinity for bracket).",
        primary_key=True) #MUST be unique on a per-tournament basis.
    mp_id = models.CharField(
        max_length=15,
        help_text="The /mp ID (not the link). Blank until match is made/finished.",
        blank=True,
        null=True)
    vod_link = models.URLField(verbose_name="Twitch VOD Link", blank=True, null=True)

    class Meta:
        ordering = ['-utc_time']

    def get_absolute_url(self):
        """Returns the url of this individual mappool."""
        return reverse('match-detail', args=[str(self.match_id)])

    def __str__(self):
        """String for representing the Model object.
        
        Returns `Stage - Team 1 vs. Team 2`."""
        return f"{self.stage} - {self.team_1.team_name} vs. {self.team_2.team_name}"

class Stage(models.Model):
    '''Model representing a stage (a group of matches on one weekend under a certain name).
    
    A stage can have many of these:
    - Match (related_name = "matches")'''

    stage_name = models.CharField(
        max_length=50,
        help_text='The stage of this tournament. Usually something like "Semifinals" or "Group Stages". '
                  'Stages occurring over different weekends should be separated, as in "Group Stages - Week 2".',
        primary_key=True) #MUST be unique on a per-tournament basis.
    date_display = models.CharField(
        max_length=50,
        help_text='The date text to display underneath the stage name, as in "Sep. 14 - Sep. 15". Has no validation.',
        blank=True)
    long_info = models.TextField(max_length=1000, help_text='Enter any special rules for this weekend.', blank=True)

    def get_absolute_url(self):
        """Returns the url of this individual mappool."""
        return reverse('stage-detail', args=[str(self.stage_name)])

    def __str__(self):
        """String for representing the Model object.

        Returns the stage name."""
        return f"{self.stage_name}"