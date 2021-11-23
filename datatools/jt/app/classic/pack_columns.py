from typing import List, Dict

from datatools.jt.model.presentation import ColumnPresentation


def pick_displayed_columns(screen_width, column_metadata_map, column_presentation_map: Dict[str, ColumnPresentation]) -> List[str]:
    """ Pick columns until they fit screen """
    result = []
    screen_width -= 1

    # simple columns first
    for k, column_presentation in column_presentation_map.items():
        renderer = column_presentation.renderers[0]
        if 0 < (renderer.max_content_width or 0) <= screen_width - 1 and not column_metadata_map[k].complex:
            result.append(k)
            screen_width -= (renderer.max_content_width + 1)

    # complex columns second
    for k, column_presentation in column_presentation_map.items():
        renderer = column_presentation.renderers[0]
        if 0 < (renderer.max_content_width or 0) <= screen_width - 1 and column_metadata_map[k].complex:
            result.append(k)
            screen_width -= (renderer.max_content_width + 1)

    return result
