import unittest
from copy import deepcopy

from aws_lambda_tools.core.masks import _apply


class MasksTestCase(unittest.TestCase):

    def setUp(self):
        self.complex_entry = {
            'id': 802830,
            'tree_top': True,
            'listy': [1, 2, 3, ],
            'nesty': {
                'id': 802830,
                'listy': [1, 2, 3, ],
                'sub_nesty': {
                    'id': 802830,
                    'listy': [1, 2, 3, ],
                },
                'immutey': ImmutableMultiDict([('access_token', '9802382302')]),
            },
            'immutey': ImmutableMultiDict([('access_token', '9802382302')]),
        }
        self.mask_value = '*' * 16

    def test_no_masking(self):
        actual = _apply(self.complex_entry)

        expected = deepcopy(self.complex_entry)
        self.assertEqual(actual, expected)

    # Nesting tests for exact field masking
    def test_mask_topmost_id_only(self):
        masked_fields = ['id']
        actual = _apply(self.complex_entry, masked_fields=masked_fields)

        expected = deepcopy(self.complex_entry)
        expected['id'] = self.mask_value
        self.assertEqual(actual, expected)

    def test_mask_nested_id_only(self):
        masked_fields = ['nesty.id']
        actual = _apply(self.complex_entry, masked_fields=masked_fields)

        expected = deepcopy(self.complex_entry)
        expected['nesty']['id'] = self.mask_value
        self.assertEqual(actual, expected)

    def test_mask_sub_nested_id_only(self):
        masked_fields = ['nesty.sub_nesty.id']
        actual = _apply(self.complex_entry, masked_fields=masked_fields)

        expected = deepcopy(self.complex_entry)
        expected['nesty']['sub_nesty']['id'] = self.mask_value
        self.assertEqual(actual, expected)
    
    # Test that entire blocks can be masked, including nested dicts
    def test_mask_list_fields(self):
        masked_fields = ['listy']
        actual = _apply(self.complex_entry, masked_fields=masked_fields)

        expected = deepcopy(self.complex_entry)
        expected['listy'] = self.mask_value
        self.assertEqual(actual, expected)
    
    def test_mask_list_fields(self):
        masked_fields = ['nesty']
        actual = _apply(self.complex_entry, masked_fields=masked_fields)

        expected = deepcopy(self.complex_entry)
        expected['nesty'] = self.mask_value
        self.assertEqual(actual, expected)

    def test_mask_list_fields(self):
        masked_fields = ['immutey']
        actual = _apply(self.complex_entry, masked_fields=masked_fields)

        expected = deepcopy(self.complex_entry)
        expected['immutey'] = self.mask_value
        self.assertEqual(actual, expected)
    
    def test_mask_list_fields(self):
        masked_fields = ['nesty.subnesty']
        actual = _apply(self.complex_entry, masked_fields=masked_fields)

        expected = deepcopy(self.complex_entry)
        expected['nesty']['subnesty'] = self.mask_value
        self.assertEqual(actual, expected)
    
    # Test that immutable dictionary contents can also be masked
    def test_mask_list_fields(self):
        masked_fields = ['immutey.access_token']
        actual = _apply(self.complex_entry, masked_fields=masked_fields)

        expected = deepcopy(self.complex_entry)
        expected['immutey'] = {'access_token': self.mask_value}
        self.assertEqual(actual, expected)
    
    def test_mask_list_fields(self):
        masked_fields = ['nesty.immutey.access_token']
        actual = _apply(self.complex_entry, masked_fields=masked_fields)

        expected = deepcopy(self.complex_entry)
        expected['nesty']['immutey'] = {'access_token': self.mask_value}
        self.assertEqual(actual, expected)

    # Test that multiple fields can be masked
    def test_mask_list_fields(self):
        masked_fields = ['tree_top', 'immutey.access_token', 'nesty.subnesty', 'nesty.id']
        actual = _apply(self.complex_entry, masked_fields=masked_fields)

        expected = deepcopy(self.complex_entry)
        expected['tree_top'] = self.mask_value
        expected['immutey'] = {'access_token': self.mask_value}
        expected['nesty']['sub_nesty'] = self.mask_value
        expected['nesty']['id'] = self.mask_value
        self.assertEqual(actual, expected)
