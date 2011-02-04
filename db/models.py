from mongoengine import *
from django import forms
from django.utils.datastructures import SortedDict

# Create your models here.

"""
class String(EmbeddedDocument):
    default = StringField()

class Text(StringField):
    pass

class Boolean(EmbeddedDocument):
    default = BooleanField()

class Integer(EmbeddedDocument):
    default = IntField()

class Float(EmbeddedDocument):
    default = FloatField()
"""

class Field(EmbeddedDocument):
    name = StringField(required = True)
    Type = StringField(choices=['string', 'text', 'email', 'boolean', 'integer', 'float'], required = True)
    required = BooleanField()

    def form_field(self):
        kwargs = {'initial': eval(str(self.default))}
        if self.Type == 'text':
            kwargs['widget'] = forms.Textarea()
        if self.Type == 'boolean':
            kwargs['required'] = False
        else:
            kwargs['required'] = self.required
        return {
                'string': forms.CharField,
                'text': forms.CharField,
                'email': forms.EmailField,
                'boolean': forms.BooleanField,
                'integer': forms.IntegerField,
                'float': forms.FloatField,
               }[self.Type](**kwargs)


class DB(Document):
    name = StringField(required = True)
    fields = ListField(EmbeddedDocumentField(Field), required = True)

    def __init__(self, *a, **kw):
        super(DB, self).__init__(*a, **kw)
        self.in_design_mode = False

    def design_form_fields(self):
        fields = SortedDict()
        fields['name'] = forms.CharField()
        fields['Type'] = forms.ChoiceField(choices = [(k, k) for k in Field.Type.choices])
        fields['required'] = forms.BooleanField(required = False)

        return fields

    def field_list(self):
        if self.in_design_mode:
            out = []
            class _f(object):
                pass

            for k, v in self.design_form_fields().items():
                f = _f()
                f.name = k
                out.append(f)
            return out

        return self.fields

    def design_entries(self):
        class FieldList(SortedDict):
            def __init__(self, n):
                self.id = '_design_field_%d' % n

            @property
            def data(self):
                return self

            @property
            def signature(self):
                return ''

        out = []
        for n, field in enumerate(self.fields):
            fl = FieldList(n)
            for f in Field._fields.keys():
                fl[f] = getattr(field, f)
            out.append(fl)

        return out

    def design_mode(self):
        self.in_design_mode = True

    def update_field(self, index, **data):
        field = Field(**data)

        if index:
            index = self._design_field_id(index)
            self.fields[index] = field
        else:
            self.fields.append(field)
            index = -1

        self.save()
        return self.design_entries()[index]

    def update_entry(self, data, signature, entry_id = None):
        if self.in_design_mode:
            return self.update_field(index = entry_id, **data)
        if entry_id:
            entry = DBEntry.objects.get(id=entry_id, db=self)
        else:
            entry = DBEntry()
        entry.db = self
        entry.data = data
        entry.signature = signature
        entry.save()
        return entry

    def _design_field_id(self, entry_id):
        return int(entry_id.replace('_design_field_', ''))

    def remove_field(self, id):
        field_n = self._design_field_id(id)
        self.fields.remove(self.fields[field_n])
        self.save()

    def remove_entry(self, entry_id):
        if self.in_design_mode:
            return self.remove_field(entry_id)
        entry = DBEntry.objects(id=entry_id, db=self)
        entry.delete()

    def as_form(self, data = None):
        form = forms.Form()

        if self.in_design_mode:
            form.fields = self.design_form_fields()
        else:
            for field in self.fields:
                form.fields[field.name] = field.form_field()

        if data:
            form.data = data
            form.is_bound = True

        return form

    def form_for_entry(self, entry_id):
        if self.in_design_mode:
            entry = self.design_entries()[self._design_field_id(entry_id)]
        else:
            entry = DBEntry.objects.get(id = entry_id, db = self)
        return self.as_form(data = entry.data)

class DBEntry(Document):
    db = ReferenceField(DB, required = True)
    data = DictField(required = True)
    signature = StringField(required = True)

    def values(self):
        return self.data.values()
