import json
import sys

from datatools.util.logging import debug
from insight.app.annotate2 import tdf_from_aggregated_json, annotate

debug('Loading data...')
data = json.load(sys.stdin)
tdf, analyse_column_present = tdf_from_aggregated_json(data, base_folder='.', out_resource_name='-')
debug(f'done')
debug(f'analyse_column_present={analyse_column_present}')
debug(f'tiers={len(tdf.schema_tiers)}')

if analyse_column_present:
    annotate(tdf)

df = tdf.resolve_df('0')
json.dump(tdf.leaves[0].to_nested_json(), fp=sys.stdout)
