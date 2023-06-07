import datetime

_LAST_DT_SUFFIX = None
_LAST_DATE_SUFFIX = None


def dtstr(use_prev=False):
    global _LAST_DT_SUFFIX
    if not (_LAST_DT_SUFFIX and use_prev):
        _LAST_DT_SUFFIX = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    return _LAST_DT_SUFFIX


def datestr(use_prev=False):
    global _LAST_DATE_SUFFIX
    if not (_LAST_DATE_SUFFIX and use_prev):
        _LAST_DATE_SUFFIX = datetime.datetime.now().strftime('%Y%m%d')
    return _LAST_DATE_SUFFIX
