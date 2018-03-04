from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.filters import FieldListFilter
from django.db.models.fields import IntegerField, AutoField
from django.db.models.fields.related import OneToOneField, ForeignKey, ManyToOneRel


class MultipleSelectFieldListFilter(FieldListFilter):

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '%s_filter' % field_path
        self.filter_statement = '%s__id' % field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_choices = field.get_choices(include_blank=False)
        super(MultipleSelectFieldListFilter, self).__init__(
            field, request, params, model, model_admin, field_path)

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def values(self):
        """
        Returns a list of values to filter on.
        """
        values = []
        value = self.used_parameters.get(self.lookup_kwarg, None)
        if value:
            values = value.split(',')
        return values

    def queryset(self, request, queryset):
        raise NotImplementedError

    def choices(self, cl):
        yield {
            'selected': self.lookup_val is None,
            'query_string': cl.get_query_string({},
                [self.lookup_kwarg]),
            'display': _('All')
        }
        for pk_val, val in self.lookup_choices:
            selected = pk_val in self.values()
            pk_list = set(self.values())
            if selected:
                pk_list.remove(pk_val)
            else:
                pk_list.add(pk_val)
            queryset_value = ','.join([str(x) for x in pk_list])
            if pk_list:
                query_string = cl.get_query_string({
                    self.lookup_kwarg: queryset_value,
                    })
            else:
                query_string = cl.get_query_string({}, [self.lookup_kwarg])
            yield {
                'selected': selected,
                'query_string': query_string,
                'display': val,
            }


class UnionFieldListFilter(MultipleSelectFieldListFilter):
    """
    A FieldListFilter which allows multiple selection of
    filters for many-to-many type fields. A list of objects will be
    returned whose m2m contains all the selected filters.
    """

    def queryset(self, request, queryset):
        filter_statement = "%s__in" % self.filter_statement
        filter_values = self.values()
        filter_dct = {
            filter_statement: filter_values
        }
        if filter_values:
            return queryset.filter(**filter_dct)
        else:
            return queryset
