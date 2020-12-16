from django.db import models

from django.urls import reverse

# Create your models here.
class Player(models.Model):
    """Model representing a player.
    
    Relationships to others (a player can have many of these):
    - Role (related_name = "roles")
    - Score (related_name = "scores)"""
    osu_id = models.CharField(
        primary_key=True,
        max_length=10, 
        help_text="The player's osu! ID.", 
        verbose_name="osu! ID")
    osu_name = models.CharField(
        max_length=30,
        help_text="The player's osu! username.", 
        verbose_name="osu! username")
    
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
        ordering = ['osu_name']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('player-detail', args=[str(self.osu_name)])

    def __str__(self):
        """String for representing the Model object.
        
        Returns their osu! ID."""
        return self.osu_id

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
    - Match (related_name = "matches)
    """
    team_name = models.CharField(max_length=100)

    #before scores exist, we sort by team name on tables and refs
    class Meta:
        ordering = ['team_name']

    def __str__(self):
        """String for representing the Model object.
        
        Returns the team name."""
        return self.team_name

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
    accuracy = models.DecimalField(max_digits=10, decimal_places=7) # ###.#######
    team_total = models.IntegerField(
        help_text="The sum of this player's score and their teammates' scores for this map on that match.")
    contrib = models.DecimalField(max_digits=10, decimal_places=7)
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

    pool = models.ForeignKey("Mappool", on_delete=models.CASCADE, related_name='maps')
    
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
    
    star_rating = models.DecimalField(max_digits=10, decimal_places=7)
    cs = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        verbose_name="AR",
        help_text="The map's circle size.")
    ar = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        verbose_name="AR",
        help_text="The map's approach rate.")
    od = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        verbose_name="AR",
        help_text="The map's overall difficulty.")
    hp = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        verbose_name="AR",
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
        verbose_name="Post-mod CS",
        help_text="The map's circle size, after applying mods.")
    ar_alt = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        blank=True,
        verbose_name="Post-mod AR",
        help_text="The map's approach rate, after applying mods.")
    od_alt = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        blank=True,
        verbose_name="Post-mod OD",
        help_text="The map's overall difficulty, after applying mods.")
    hp_alt = models.DecimalField(
        max_digits=5, 
        decimal_places=3,
        blank=True,
        verbose_name="Post-mod HP",
        help_text="The map's HP drain, after applying mods.")
    duration_alt = models.IntegerField(
        verbose_name="Post-mod drain time",
        help_text = "Map's drain time in seconds.",
        blank=True
    )

    def __str__(self):
        """String representation of a map.
        
        Returns `Artist - Title [Difficulty] (Mapper).`"""
        return f"{self.artist} - {self.title} [{self.diff_name}] ({self.creator})"

    def long_name(self):
        """Longer string representation of a map.
        
        Intended for use with tooltips.
        Returns `Mappool stage/name, pool ID: Artist - Title [Difficulty] (set creator).`"""
        return f"{self.pool}, {self.pool_id}: {self.artist} - {self.title} [{self.diff_name}] ({self.creator})"


