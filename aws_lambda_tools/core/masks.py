import json
from copy import deepcopy
from collections import Iterable

from werkzeug.datastructures import ImmutableMultiDict

def _build_key_chain(key_chain, key=None):
    if key_chain is None:
        return key

    return '.'.join([key_chain, key])

def _apply(entry, masked_fields=None, key_chain=None):
    """
    Recursively run through the event (dict) until all desired fields are masked
    :params entry: <dict> of some form. Can be heavily nested
    :params masked_fields: <list> of fields to mask (dotted notation for nested fields)
    :params key_chain: <string> string to track the chain of parent keys, to make sure we
        mask exactly the specified key chain.
    """
    for key, value in entry.items():
        for masked_field in masked_fields:
            # e.g. 'body.access_token'
            if masked_field in [key_chain, _build_key_chain(key_chain, key=key)]:
                # Exact field found
                entry[key] = '*' * 16
                break

            if key in masked_field:
                # Must dig deeper into the nest
                if isinstance(value, ImmutableMultiDict):
                    value = value.to_dict(flat=False)

                if isinstance(value, dict):
                    key_chain = _build_key_chain(key_chain, key=key)

                    # recurse through sub-dict till we hit the final key-value pair
                    entry[key] = _apply(value, masked_fields=masked_fields, key_chain=key_chain)

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
        if isinstance(entry, Iterable)
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
        if isinstance(entry, Iterable)
    ]
