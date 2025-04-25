import datetime
import re
from markupsafe import Markup


def format_datetime_filter(value, format="%Y-%m-%d %H:%M"):
    """Formats an ISO datetime string."""
    if not value:
        return ""
    try:
        dt_obj = datetime.datetime.fromisoformat(str(value))
        return dt_obj.strftime(format)
    except (ValueError, TypeError):
        return value


def nl2br_filter(s):
    """Converts newlines in a string to HTML <br> tags."""
    if s:
        s = re.sub(r"(\r\n|\r|\n)", "<br>\n", s)
        return Markup(s)
    return ""
