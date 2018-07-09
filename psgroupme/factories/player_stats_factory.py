from parsers.player_stats.sportsengine_player_stats \
    import SportsEnginePlayerStats


class PlayerStatsFactory(object):

    def create(stats_type, **kwargs):
        if stats_type == 'sportsengine':
            return SportsEnginePlayerStats(**kwargs)
        else:
            raise ValueError("Schedule Type '{0}' not found"
                             .format(stats_type))

    create = staticmethod(create)


def main(stats_type='sportsengine'):
    """
    This is more of a testing procedure.  Get all relevent info and print it
    """
    sched_kwargs = {
        'team_id': 3367048,
        'season_id': 481539,
        'company': 'dreamsports'
    }
    stats = PlayerStatsFactory.create(stats_type, **sched_kwargs)
    print(stats)


if __name__ == "__main__":
    main()
