from parsers.rsvp_tools.benchapp import BenchApp


class FinanceToolFactory(object):

    def create(finance_tool_type, **kwargs):
        if finance_tool_type == 'benchapp':
            return BenchApp(**kwargs)
        else:
            raise ValueError("Finance Tool Type '{0}' not found"
                             .format(finance_tool_type))

    create = staticmethod(create)
