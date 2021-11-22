import datetime


def fit_time_bar(min_pos, max_pos, n_chars, stripes_per_char, build_bar: bool = True):
    n_stripes = n_chars * stripes_per_char
    x_axis_amount_per_stripe = compute_x_axis_amount_per_stripe(min_pos, max_pos, n_stripes)
    if x_axis_amount_per_stripe == 0:
        x_axis_amount_per_stripe = 1    # hack, perhaps, min_pos == max_pos

    if is_same_date(min_pos, max_pos):
        if is_same_minute(min_pos, max_pos):
            label_length_chars = 2
            time_format = "%S"
        else:
            label_length_chars = 5
            time_format = "%H:%M"
    else:
        label_length_chars = 16
        time_format = "%Y-%m-%d %H:%M"

    stride_of_marks_in_chars = label_length_chars + 2  # 2 spaces between labels
    x_axis_unit_per_mark = x_axis_amount_per_stripe * stripes_per_char * stride_of_marks_in_chars
    x_axis_unit_per_mark = compute_better_time_unit(x_axis_unit_per_mark)  # TODO better non-time units
    x_axis_amount_per_char = x_axis_unit_per_mark / stride_of_marks_in_chars
    x_axis_amount_per_stripe = x_axis_amount_per_char / stripes_per_char
    n_chars = int(0.999999 + (max_pos - min_pos) / x_axis_amount_per_char)
    n_stripes = n_chars * stripes_per_char

    bar = None if not build_bar else time_bar(
        datetime.datetime.fromtimestamp(min_pos),
        datetime.timedelta(milliseconds=1000 * x_axis_amount_per_char * stride_of_marks_in_chars),
        time_format,
        n_marks=n_chars // stride_of_marks_in_chars,
        n_separator_spaces=stride_of_marks_in_chars - label_length_chars
    )
    return bar, n_stripes, x_axis_amount_per_stripe


def is_same_date(ts1, ts2):
    return datetime.datetime.fromtimestamp(ts1).date() == datetime.datetime.fromtimestamp(ts2).date()


def is_same_minute(ts1, ts2):
    dt1 = datetime.datetime.fromtimestamp(ts1)
    dt2 = datetime.datetime.fromtimestamp(ts2)
    return dt1.date() == dt2.date() and dt1.hour == dt2.hour and dt1.minute == dt2.minute


def compute_x_axis_amount_per_stripe(min_pos, max_pos, n_stripes):
    """ Computes "position unit" per stripe """
    pos_unit = (max_pos - min_pos) / n_stripes
    return pos_unit


def time_bar(start_time: datetime, time_delta: datetime.timedelta, t_format, n_marks, n_separator_spaces):
    result = ""
    now = start_time

    for i in range(n_marks):
        result += now.strftime(t_format)
        result += ' ' * n_separator_spaces
        now += time_delta
    return result


def compute_better_time_unit(time_unit):
    """ time_unit: seconds """
    if time_unit <= 0.25:
        return 0.25
    elif 0.25 < time_unit <= 0.5:
        return 0.5
    elif 0.5 < time_unit <= 1:
        return 1
    elif 1 < time_unit <= 2:
        return 2
    elif 2 < time_unit <= 5:
        return 5
    elif 5 < time_unit <= 10:
        return 10
    elif 10 < time_unit <= 15:
        return 15
    elif 15 < time_unit <= 20:
        return 20
    elif 20 < time_unit <= 30:
        return 30
    elif 30 < time_unit <= 60:
        return 60
    elif 1 * 60 < time_unit <= 2 * 60:
        return 2 * 60
    elif 2 * 60 < time_unit <= 5 * 60:
        return 5 * 60
    elif 5 * 60 < time_unit <= 10 * 60:
        return 10 * 60
    elif 10 * 60 < time_unit <= 15 * 60:
        return 15 * 60
    elif 15 * 60 < time_unit <= 20 * 60:
        return 20 * 60
    elif 20 * 60 < time_unit <= 30 * 60:
        return 30 * 60
    elif 30 * 60 < time_unit <= 45 * 60:
        return 45 * 60
    elif 45 * 60 < time_unit <= 60 * 60:
        return 60 * 60
    elif 60 * 60 < time_unit <= 90 * 60:  # 1.5 hours
        return 90 * 60
    elif 90 * 60 < time_unit <= 120 * 60:  # 2 hours
        return 120 * 60
    elif 120 * 60 < time_unit <= 180 * 60:  # 3 hours
        return 120 * 60
    elif 180 * 60 < time_unit <= 240 * 60:  # 4 hours
        return 240 * 60
    elif 4 * 60 * 60 < time_unit <= 6 * 60 * 60:  # 6 hours
        return 6 * 60 * 60
    elif 6 * 60 * 60 < time_unit <= 8 * 60 * 60:  # 8 hours
        return 8 * 60 * 60
    elif 8 * 60 * 60 < time_unit <= 12 * 60 * 60:  # 12 hours
        return 12 * 60 * 60
    elif 12 * 60 * 60 < time_unit <= 24 * 60 * 60:  # 24 hours
        return 24 * 60 * 60
    elif 24 * 60 * 60 < time_unit <= 48 * 60 * 60:  # 48 hours
        return 48 * 60 * 60
    else:
        return time_unit
