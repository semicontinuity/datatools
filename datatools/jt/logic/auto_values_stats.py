from datatools.json.util import is_primitive


def compute_value_stats(data, stats_map):
    for record in data:
        for key, value in record.items():
            stats = stats_map[key]
            if stats.count is None:
                stats.count = 0
            stats.count += 1

            if value is ... or value is None or not is_primitive(value):
                del stats_map[key]

            value_as_string = str(value)

            dict_index = stats.dictionary.get(value_as_string)
            if dict_index is None:
                dict_index = len(stats.dictionary)
            stats.dictionary[value_as_string] = dict_index

            non_unique_value_count = stats.non_unique_value_counts.get(value_as_string)
            if non_unique_value_count is None:
                if value_as_string in stats.unique_values:
                    stats.unique_values.remove(value_as_string)
                    stats.non_unique_value_counts[value_as_string] = 2
                else:
                    stats.unique_values.add(value_as_string)
            else:
                stats.non_unique_value_counts[value_as_string] = non_unique_value_count + 1
