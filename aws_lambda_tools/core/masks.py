import json
from copy import deepcopy

from werkzeug.datastructures import ImmutableMultiDict


def _apply(entry, masked_fields=None):
    for key, value in entry.items():
        for masked_field in masked_fields:
            # e.g. 'body.access_token'
            if key in masked_field:
                if isinstance(value, ImmutableMultiDict):
                    value = value.to_dict(flat=False)

                if isinstance(value, dict):
                    # recurse through sub-dict till we hit the final key-value pair
                    entry[key] = _apply(value, masked_fields=masked_fields)
                else:
                    # final key-pair pair found
                    entry[key] = '*' * 16

    return entry


def _input(*args, **kwargs):
    masked_fields = kwargs.pop('masked_fields')

    if not masked_fields.get('input'):
        return args, kwargs

    masked_fields = masked_fields['input']

    # At the time of writing, kwargs and never parsed. So just masking arg entries for now
    logged_args = [
        _apply(
            deepcopy(entry), masked_fields=masked_fields
        )
        for entry in args
    ]

    return logged_args, kwargs


def _output(result, masked_fields=None):
    if not masked_fields.get('output'):
        return result

    masked_fields = masked_fields['output']

    result['body'] = json.loads(result['body'])
    result = deepcopy(result)

    if isinstance(result, dict):
        # Single entry in output
        return _apply(result, masked_fields=masked_fields)

    # Multiple entries in output
    return [
        _apply(entry, masked_fields=masked_fields)
        for entry in result
    ]
