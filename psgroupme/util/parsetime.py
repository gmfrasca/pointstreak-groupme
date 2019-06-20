import parsedatetime as pdt
import datetime


DATE_DESCRIPTOR = "%a, %b %d"
# TIME_DESCRIPTOR = "%H:%M"  # 24-hour
TIME_DESCRIPTOR = "%I:%M %p"  # 12-hour
FULL_DESCRIPTOR = "{0} {1}".format(DATE_DESCRIPTOR, TIME_DESCRIPTOR)
FINAL_DESCRIPTOR = "{0} (FINAL)".format(DATE_DESCRIPTOR)

# TIME_DESCRIPTOR = "%a %b %d %H:%M"  # 24-hour
# TIME_DESCRIPTOR = "%a %b %d %I:%M%p"  # 12-hour


def determine_year(year=None):
    if year is None:
        year = datetime.datetime.now().year
    return str(year)


def normalize_date(date, year=None, includes_day=False, return_type=str):
    cut_item = 1 if includes_day else 0
    year = determine_year(year)
    listdate = date.split()[cut_item:]
    listdate.extend([year])
    strdate = '{} {} {}'.format(*listdate)  # TODO: handle len(listdate) != 3
    parsed, status = pdt.Calendar(
        version=pdt.VERSION_CONTEXT_STYLE).parseDT(str(strdate))
    if return_type == str:
        return parsed.strftime(DATE_DESCRIPTOR)
    return parsed


def normalize_time(time, return_type=str):
    parsed, status = pdt.Calendar(
        version=pdt.VERSION_CONTEXT_STYLE).parseDT(str(time))
    if return_type == str:
        return parsed.strftime(TIME_DESCRIPTOR)
    return parsed


def assemble_full_datetime(date, time, year=None):
    """
    Get a parsable full gametime (date + time) based on a
    human-readable date (ex: Wed, Aug 5) and Time

    Args:
        date (str): A human-readable date string, like 'Wed, Aug 5'
        time (str): A human-readable time string, like '8:45 PM'

    Returns:
        a parsed pdt object representing the input date and time
    """
    year = determine_year(year)
    fulltime = date.split()[1:]
    fulltime.extend([year])
    fulltime.extend(time.split())
    fulltime = ' '.join(fulltime)

    # TODO: act on bad status from parseDT
    parsed, status = pdt.Calendar(
        version=pdt.VERSION_CONTEXT_STYLE).parseDT(str(fulltime))
    return parsed
