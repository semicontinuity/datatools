import datetime


def parse_timestamp(ts):
    """
    Auto-detect time format and parse it with datetime (to be able to run on machines with no bare python installed)
    supported formats:
    %H:%M:%S
    %Y-%m-%d %H:%M:%S
    %Y-%m-%d %H:%M:%S.%f
    %Y-%m-%d %H:%M:%S.%f%z
    ISO
    """
    res = infer_timestamp_format(ts)
    if res == 'ISO':
        return datetime.datetime.fromisoformat(ts).timestamp()
    print(res)
    pattern, _ = res
    return datetime.datetime.strptime(ts, pattern).timestamp()


def infer_timestamp_format(ts):
    if ts is None or len(ts) < 5:
        return None, ts
    # pre-3.7 python cannot parse tz with colon!
    if len(ts) >= 6 and ":" == ts[-3] and "+" == ts[-6]:
        ts = ts[:-3] + ts[-2:]

    date_offset = None
    sep_char = None
    time_offset = None
    fraction_char = None
    has_tz_offset = None
    if ts[2] == ':' and ts[:2].isdigit():
        time_offset = 0
    if ts[4] == '-' and ts[:4].isdigit():
        date_offset = 0
    if len(ts) >= 19 and date_offset is not None:
        sep_char = ts[10]
        time_offset = 11
    if time_offset is not None:
        if len(ts) - time_offset > 8 and (ts[time_offset + 8] == '.' or ts[time_offset + 8] == ','):
            fraction_char = ts[time_offset + 8]
        if ts.find('+') >= 0 or ts.find('Z') >= 0:
            has_tz_offset = True

    pattern = ''
    if date_offset is not None: pattern = pattern + '%Y-%m-%d'
    if sep_char is not None: pattern = pattern + sep_char
    if time_offset is not None: pattern = pattern + '%H:%M:%S'
    if fraction_char: pattern = pattern + fraction_char + '%f'
    if has_tz_offset is not None: pattern = pattern + '%z'
    if pattern and len(ts) == 30:
        return 'ISO'
    return pattern if pattern != '' else None, ts
