from typing import List, Dict

from datatools.jt.auto_presentation import ColumnPresentation


def pick_displayed_columns(screen_width, column_metadata_map, column_presentation_map: Dict[str, ColumnPresentation]) -> List[str]:
    """ Pick columns until they fit screen """
    result = []
    screen_width -= 1

    # simple columns first
    for k, column_presentation in column_presentation_map.items():
        if 0 < column_presentation.max_length <= screen_width - 1 and not column_metadata_map[k].complex:
            result.append(k)
            screen_width -= (column_presentation.max_length + 1)

    # complex columns second
    for k, column_presentation in column_presentation_map.items():
        if 0 < column_presentation.max_length <= screen_width - 1 and column_metadata_map[k].complex:
            result.append(k)
            screen_width -= (column_presentation.max_length + 1)

    return result
