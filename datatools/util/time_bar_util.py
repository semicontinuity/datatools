import datetime


def fit_time_bar(min_pos, max_pos, n_chars, stripes_per_char):
    n_stripes = n_chars * stripes_per_char
    x_axis_amount_per_stripe = compute_x_axis_amount_per_stripe(min_pos, max_pos, n_stripes)
    label_length_chars = 5 if is_same_date(min_pos, max_pos) else 16
    time_format = "%H:%M" if is_same_date(max_pos, min_pos) else "%Y-%m-%d %H:%M"

    stride_of_marks_in_chars = label_length_chars + 2  # 2 spaces between labels
    x_axis_unit_per_mark = x_axis_amount_per_stripe * stripes_per_char * stride_of_marks_in_chars
    x_axis_unit_per_mark = compute_better_time_unit(x_axis_unit_per_mark)  # TODO better non-time units
    x_axis_amount_per_char = x_axis_unit_per_mark / stride_of_marks_in_chars
    x_axis_amount_per_stripe = x_axis_amount_per_char / stripes_per_char
    n_chars = int((max_pos - min_pos) / x_axis_amount_per_stripe / stripes_per_char)
    n_stripes = n_chars * stripes_per_char

    bar = time_bar(
        datetime.datetime.fromtimestamp(min_pos),
        datetime.timedelta(milliseconds=1000 * x_axis_amount_per_char * stride_of_marks_in_chars),
        time_format,
        n_marks=n_chars // stride_of_marks_in_chars,
        n_separator_spaces=stride_of_marks_in_chars - label_length_chars
    )
    return bar, n_stripes, x_axis_amount_per_stripe


def is_same_date(ts1, ts2):
    return datetime.datetime.fromtimestamp(ts1).date() == datetime.datetime.fromtimestamp(ts2).date()


def compute_x_axis_amount_per_stripe(min_pos, max_pos, n_stripes):
    """ Computes "position unit" per stripe """

    pos_unit = (max_pos - min_pos) / (n_stripes - 1)    # width - 1? some kind of rounding?

    # some rounding
    return ((pos_unit + 0.999999) // 1) * 1


def time_bar(start_time: datetime, time_delta: datetime.timedelta, format, n_marks, n_separator_spaces):
    result = ""
    now = start_time

    for i in range(n_marks):
        result += now.strftime(format)
        result += ' ' * n_separator_spaces
        now += time_delta
    return result


def compute_better_time_unit(time_unit):
    """ time_unit: seconds """
    if time_unit > 15 * 60 and time_unit <= 20 * 60:
        return 20 * 60
    if time_unit > 20 * 60 and time_unit <= 30 * 60:
        return 30 * 60
    elif time_unit > 30 * 60 and time_unit <= 45 * 60:
        return 45 * 60
    elif time_unit > 45 * 60 and time_unit <= 60 * 60:
        return 60 * 60
    elif time_unit > 60 * 60 and time_unit <= 90 * 60:  # 1.5 hours
        return 90 * 60
    elif time_unit > 90 * 60 and time_unit <= 120 * 60:  # 2 hours
        return 120 * 60
    elif time_unit > 120 * 60 and time_unit <= 180 * 60:  # 3 hours
        return 120 * 60
    elif time_unit > 180 * 60 and time_unit <= 240 * 60:  # 4 hours
        return 240 * 60
    elif time_unit > 4 * 60 * 60 and time_unit <= 6 * 60 * 60:  # 6 hours
        return 6 * 60 * 60
    elif time_unit > 6 * 60 * 60 and time_unit <= 8 * 60 * 60:  # 8 hours
        return 8 * 60 * 60
    elif time_unit > 8 * 60 * 60 and time_unit <= 12 * 60 * 60:  # 12 hours
        return 12 * 60 * 60
    elif time_unit > 12 * 60 * 60 and time_unit <= 24 * 60 * 60:  # 24 hours
        return 24 * 60 * 60
    elif time_unit > 24 * 60 * 60 and time_unit <= 48 * 60 * 60:  # 48 hours
        return 48 * 60 * 60
    else:
        return time_unit
