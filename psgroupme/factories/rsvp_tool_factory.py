from parsers.rsvp_tools.team_locker_room import TeamLockerRoom
from parsers.rsvp_tools.benchapp import BenchApp


class RsvpToolFactory(object):

    def create(rsvp_tool_type, **kwargs):
        if rsvp_tool_type == 'teamlockerroom' or rsvp_tool_type == 'tlr':
            return TeamLockerRoom(**kwargs)
        if rsvp_tool_type == 'benchapp':
            return BenchApp(**kwargs)
        else:
            raise ValueError("RSVP Tool Type '{0}' not found"
                             .format(rsvp_tool_type))

    create = staticmethod(create)
