from parsers.schedules.pointstreak_schedule import PointstreakSchedule
from parsers.schedules.sportsengine_schedule import SportsEngineSchedule
from parsers.schedules.dashplatform_schedule import DashPlatformSchedule
from parsers.schedules.debug_schedule import DebugSchedule
from parsers.schedules.debug_schedule import ScoreUpdateDebugSchedule
from parsers.schedules.debug_schedule import TimeUpdateDebugSchedule
from parsers.schedules.debug_schedule import GameAddDebugSchedule
from parsers.schedules.debug_schedule import GameRemoveDebugSchedule
import datetime


class ScheduleFactory(object):

    def create(schedule_type, **kwargs):
        if schedule_type == 'pointstreak':
            return PointstreakSchedule(**kwargs)
        elif schedule_type == 'sportsengine':
            return SportsEngineSchedule(**kwargs)
        elif schedule_type == 'dash':
            return DashPlatformSchedule(**kwargs)
        elif schedule_type == 'debug':
            return DebugSchedule(**kwargs)
        elif schedule_type == 'debug_scoreupdate':
            return ScoreUpdateDebugSchedule(**kwargs)
        elif schedule_type == 'debug_timeupdate':
            return TimeUpdateDebugSchedule(**kwargs)
        elif schedule_type == 'debug_gameadd':
            return GameAddDebugSchedule(**kwargs)
        elif schedule_type == 'debug_gameremove':
            return GameRemoveDebugSchedule(**kwargs)
        else:
            raise ValueError("Schedule Type '{0}' not found"
                             .format(schedule_type))

    create = staticmethod(create)


def main(schedule_type='sportsengine'):
    """
    This is more of a testing procedure.  Get all relevent info and print it
    """
    sched_kwargs = {
        'team_id': 3367048,
        'season_id': 481539,
        'company': 'dreamsports'
    }
    schedule = ScheduleFactory.create(schedule_type, **sched_kwargs)
    now = datetime.datetime.now()
    next_game = schedule.get_next_game()
    last_game = schedule.get_last_game()
    print "--- Today's Date ---"
    print now
    print "--- Full Schedule ---"
    print schedule.get_schedule()
    print "--- Next Game on Schedule ---"
    if not next_game:
        print 'No games left on schedule'
    else:
        print 'The next game is {0}'.format(next_game)
    print "--- Last Game Played ---"
    if not last_game:
        print 'No games have been played yet'
    else:
        print 'The last game was {0}'.format(last_game)


if __name__ == "__main__":
    main()
