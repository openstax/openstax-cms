from django.test import TestCase

from extraadminfilters.filters import UnionFieldListFilter


class FilterTests(TestCase):

    def test_create_union_field_filter(self):
        list_filter = [
            ("book", UnionFieldListFilter),
        ]
        self.assertEquals(list_filter[0][1], UnionFieldListFilter)
