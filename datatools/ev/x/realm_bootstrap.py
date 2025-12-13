import os
from pathlib import Path

from datatools.ev.util.entity_reference_chain import ctx_to_resources


def get_realm_ctx(props):
    return str(
        ctx_to_resources(ctx=Path(get_ctx(props)).parent, ctx_dir=Path(props['CTX_DIR']))[-1]
    )


def get_realm_ctx_dir(props):
    return os.path.abspath(props.get('CTX_DIR') + '/' + get_ctx(props) + '/..')


def get_ctx(props):
    return props.get('CTX_BASE') or props.get('CTX')

