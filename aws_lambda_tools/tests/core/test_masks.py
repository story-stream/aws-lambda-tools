import unittest
from copy import deepcopy
from werkzeug.datastructures import ImmutableMultiDict

from aws_lambda_tools.core.masks import _apply


class MasksTestCase(unittest.TestCase):

    def setUp(self):
        self.mask_value = '*' * 16

    def test_no_masking(self):
        expected = {
            'id': 802830,
        }

        mock_entry = {
            'id': 802830,
        }

        masked_fields = []
        actual = _apply(mock_entry, masked_fields=masked_fields)

        self.assertEqual(actual, expected)

    # Nesting tests for exact field masking
    def test_mask_topmost_id_only(self):
        expected = {
            'id': self.mask_value,
        }

        mock_entry = {
            'id': 802830,
        }

        masked_fields = ['id']
        actual = _apply(mock_entry, masked_fields=masked_fields)

        self.assertEqual(actual, expected)

    def test_mask_nested_id_only(self):
        expected = {
            'nesty': {
                'id': self.mask_value,
            }
        }

        mock_entry = {
            'nesty': {
                'id': 802830,
            }
        }

        masked_fields = ['nesty.id']
        actual = _apply(mock_entry, masked_fields=masked_fields)

        self.assertEqual(actual, expected)

    def test_mask_sub_nested_id_only(self):
        expected = {
            'nesty': {
                'sub_nesty': {
                    'id': self.mask_value,
                }
            }
        }

        mock_entry = {
            'nesty': {
                'sub_nesty': {
                    'id': 802830,
                }
            }
        }

        masked_fields = ['nesty.sub_nesty.id']
        actual = _apply(mock_entry, masked_fields=masked_fields)

        self.assertEqual(actual, expected)
    
    # Test that entire blocks can be masked, including nested dicts
    def test_mask_list_valued_field(self):
        expected = {
            'listy': self.mask_value,
        }

        mock_entry = {
            'listy': [1, 2, 3, ]
        }

        masked_fields = ['listy']
        actual = _apply(mock_entry, masked_fields=masked_fields)

        self.assertEqual(actual, expected)
    
    def test_mask_nested_dictionary(self):
        expected = {
            'nesty': self.mask_value,
        }

        mock_entry = {
            'nesty': {
                'id': 802830,
            }
        }

        masked_fields = ['nesty']
        actual = _apply(mock_entry, masked_fields=masked_fields)

        self.assertEqual(actual, expected)

    def test_mask_immutable_dictionary(self):
        expected = {
            'immutey': self.mask_value,
        }

        mock_entry = {
            'immutey': ImmutableMultiDict([('access_token', '9802382302')]),
        }

        masked_fields = ['immutey']
        actual = _apply(mock_entry, masked_fields=masked_fields)

        self.assertEqual(actual, expected)
    
    def test_mask_doubly_nested_dictionary(self):
        expected = {
            'nesty': {
                'sub_nesty': self.mask_value,
            }
        }

        mock_entry = {
            'nesty': {
                'sub_nesty': {
                    'id': 802830,
                }
            }
        }
        
        masked_fields = ['nesty.sub_nesty']
        actual = _apply(mock_entry, masked_fields=masked_fields)

        self.assertEqual(actual, expected)
    
    # Test that immutable dictionary contents can also be masked
    def test_mask_field_in_immutable_dictionary(self):
        expected = {
            'immutey': {
                'access_token': self.mask_value,
            }
        }

        mock_entry = {
            'immutey': ImmutableMultiDict([('access_token', '9802382302')]),
        }
        
        masked_fields = ['immutey.access_token']
        actual = _apply(mock_entry, masked_fields=masked_fields)

        self.assertEqual(actual, expected)
    
    def test_mask_field_in_nested_immutable_dictionary(self):
        expected = {
            'nesty': {
                'immutey': {
                    'access_token': self.mask_value,
                },
            }
        }

        mock_entry = {
            'nesty': {
                'immutey': ImmutableMultiDict([('access_token', '9802382302')]),
            }
        }

        masked_fields = ['nesty.immutey.access_token']
        actual = _apply(mock_entry, masked_fields=masked_fields)

        self.assertEqual(actual, expected)

    # Test that multiple fields can be masked
    # def test_mask_multiple_fields(self):
    #     expected = {
    #         'id': 802830,
    #         'tree_top': self.mask_value,
    #         'immutey': {
    #             'access_token': self.mask_value,
    #         },
    #         'nesty': {
    #             'id': self.mask_value,
    #             'sub_nesty': self.mask_value,
    #         },
    #     }

    #     mock_entry = {
    #         'id': 802830,
    #         'tree_top': True,
    #         'immutey': ImmutableMultiDict([('access_token', '9802382302')]),
    #         'nesty': {
    #             'id': 802830,
    #             'sub_nesty': {
    #                 'id': 802830,
    #             },
    #         },
    #     }

    #     masked_fields = ['tree_top', 'immutey.access_token', 'nesty.sub_nesty', 'nesty.id']
    #     actual = _apply(mock_entry, masked_fields=masked_fields)

    #     self.assertEqual(actual, expected)
