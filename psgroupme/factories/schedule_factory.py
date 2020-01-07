from recleagueparser.schedules.pointstreak_schedule import (
    PointstreakSchedule)
from recleagueparser.schedules.sportsengine_schedule import (
    SportsEngineSchedule)
from recleagueparser.schedules.dashplatform_schedule import (
    DashPlatformSchedule)
from recleagueparser.schedules.debug_schedule import (
    DebugSchedule, ScoreUpdateDebugSchedule, TimeUpdateDebugSchedule,
    GameAddDebugSchedule, GameRemoveDebugSchedule, GameFinalizedDebugSchedule)


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
        elif schedule_type == 'debug_gamefinal':
            return GameFinalizedDebugSchedule(**kwargs)
        else:
            raise ValueError("Schedule Type '{0}' not found"
                             .format(schedule_type))

    create = staticmethod(create)
