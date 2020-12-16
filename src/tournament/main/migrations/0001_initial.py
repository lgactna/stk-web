# Generated by Django 3.1.4 on 2020-12-16 05:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Map',
            fields=[
                ('diff_id', models.CharField(help_text='The difficulty ID for this map, as in osu.ppy.sh/b/<id>', max_length=15, primary_key=True, serialize=False, verbose_name='Difficulty ID')),
                ('set_id', models.CharField(help_text='The set ID for this map, as in osu.ppy.sh/s/<id>', max_length=15, verbose_name='Beatmap Set ID')),
                ('pool_id', models.CharField(help_text='The mod pool+numerical ID of this map, as in NM1, DT2, etc.', max_length=5)),
                ('map_type', models.CharField(choices=[('NM', 'Nomod'), ('HD', 'Hidden'), ('HR', 'HardRock'), ('DT', 'DoubleTime'), ('FM', 'FreeMod'), ('TB', 'Tiebreaker')], help_text='The mod this pool belongs in (NM, HR, etc.) TB is a separate "mod".', max_length=2)),
                ('artist', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=100)),
                ('diff_name', models.CharField(max_length=100)),
                ('creator', models.CharField(max_length=100)),
                ('star_rating', models.DecimalField(decimal_places=7, max_digits=10)),
                ('cs', models.DecimalField(decimal_places=3, help_text="The map's circle size.", max_digits=5, verbose_name='AR')),
                ('ar', models.DecimalField(decimal_places=3, help_text="The map's approach rate.", max_digits=5, verbose_name='AR')),
                ('od', models.DecimalField(decimal_places=3, help_text="The map's overall difficulty.", max_digits=5, verbose_name='AR')),
                ('hp', models.DecimalField(decimal_places=3, help_text="The map's HP drain.", max_digits=5, verbose_name='AR')),
                ('duration', models.IntegerField(help_text="Map's drain time in seconds.", verbose_name='Drain time')),
                ('cs_alt', models.DecimalField(blank=True, decimal_places=3, help_text="The map's circle size, after applying mods.", max_digits=5, verbose_name='Post-mod CS')),
                ('ar_alt', models.DecimalField(blank=True, decimal_places=3, help_text="The map's approach rate, after applying mods.", max_digits=5, verbose_name='Post-mod AR')),
                ('od_alt', models.DecimalField(blank=True, decimal_places=3, help_text="The map's overall difficulty, after applying mods.", max_digits=5, verbose_name='Post-mod OD')),
                ('hp_alt', models.DecimalField(blank=True, decimal_places=3, help_text="The map's HP drain, after applying mods.", max_digits=5, verbose_name='Post-mod HP')),
                ('duration_alt', models.IntegerField(blank=True, help_text="Map's drain time in seconds.", verbose_name='Post-mod drain time')),
            ],
        ),
        migrations.CreateModel(
            name='Mappool',
            fields=[
                ('display_order', models.IntegerField(help_text='What index this pool is, unique. Pools are ordered highest first.', primary_key=True, serialize=False)),
                ('mappool_name', models.CharField(help_text='The full name of this mappool (as in Grand Finals).', max_length=100)),
                ('short_name', models.CharField(help_text='The shorthand name for this mappool (as in SF, Ro32, etc.)', max_length=10)),
                ('display_color', models.CharField(help_text='RGBA hex (as #RRGGBBAA), webpage-compatible.', max_length=9)),
            ],
            options={
                'ordering': ['-display_order'],
            },
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('utc_time', models.DateTimeField(blank=True, verbose_name='UTC Time')),
                ('match_id', models.CharField(blank=True, help_text='The internal match ID of the tournament (usually A1, B1, C2 for GS, 1-infinity for bracket).', max_length=5, primary_key=True, serialize=False)),
                ('mp_id', models.CharField(blank=True, help_text='The /mp ID (not the link). Blank until match is made/finished.', max_length=15)),
                ('vod_link', models.URLField(verbose_name='Twitch VOD Link')),
            ],
            options={
                'ordering': ['-utc_time'],
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('osu_id', models.CharField(help_text="The player's osu! ID.", max_length=10, primary_key=True, serialize=False, verbose_name='osu! ID')),
                ('osu_name', models.CharField(help_text="The player's osu! username.", max_length=30, verbose_name='osu! username')),
                ('is_staff', models.BooleanField(help_text='Whether this user is a staff member or not.', verbose_name='Player is staff?')),
                ('discord_name', models.CharField(help_text="The player's Discord tag (with discriminator).", max_length=100)),
            ],
            options={
                'ordering': ['osu_name'],
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('role_name', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('role_color', models.CharField(help_text='RGBA hex (as #RRGGBBAA), webpage-compatible.', max_length=9)),
                ('is_staff', models.BooleanField(help_text='Is this role staff-related? (has no effect on Player.is_staff)')),
            ],
        ),
        migrations.CreateModel(
            name='Stage',
            fields=[
                ('stage_name', models.CharField(help_text='The stage of this tournament. Usually something like "Semifinals" or "Group Stages". Stages occurring over different weekends should be separated, as in "Group Stages - Week 2".', max_length=50, primary_key=True, serialize=False)),
                ('date_display', models.CharField(blank=True, help_text='The date text to display underneath the stage name, as in "Sep. 14 - Sep. 15". Has no validation.', max_length=50)),
                ('long_info', models.TextField(blank=True, help_text='Enter any special rules for this weekend.', max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_name', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['team_name'],
            },
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_index', models.IntegerField(help_text='The index of this score relative to the match, zero-indexed.')),
                ('score', models.IntegerField(help_text='The actual score value.')),
                ('combo', models.IntegerField()),
                ('accuracy', models.DecimalField(decimal_places=7, max_digits=10)),
                ('team_total', models.IntegerField(help_text="The sum of this player's score and their teammates' scores for this map on that match.")),
                ('contrib', models.DecimalField(decimal_places=7, max_digits=10)),
                ('count_300', models.IntegerField(verbose_name='300s')),
                ('count_100', models.IntegerField(verbose_name='100s')),
                ('count_50', models.IntegerField(verbose_name='50s')),
                ('count_miss', models.IntegerField(verbose_name='Misses')),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='scores', to='main.map')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='main.match')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='main.player')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='main.team')),
            ],
            options={
                'ordering': ['score', 'accuracy'],
            },
        ),
        migrations.AddField(
            model_name='player',
            name='team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='players', to='main.team'),
        ),
        migrations.AddField(
            model_name='match',
            name='commentators',
            field=models.ManyToManyField(blank=True, related_name='commentated_matches', to='main.Player'),
        ),
        migrations.AddField(
            model_name='match',
            name='mappool',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='matches', to='main.mappool'),
        ),
        migrations.AddField(
            model_name='match',
            name='referee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reffed_matches', to='main.player'),
        ),
        migrations.AddField(
            model_name='match',
            name='stage',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='matches', to='main.stage'),
        ),
        migrations.AddField(
            model_name='match',
            name='streamer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='streamed_matches', to='main.player'),
        ),
        migrations.AddField(
            model_name='match',
            name='team_1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='matches_1', to='main.team'),
        ),
        migrations.AddField(
            model_name='match',
            name='team_2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='matches_2', to='main.team'),
        ),
        migrations.AddField(
            model_name='map',
            name='mappool',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='maps', to='main.mappool'),
        ),
    ]