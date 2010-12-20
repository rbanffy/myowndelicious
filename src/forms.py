# -*- coding:utf-8 -*-

# We are using an ancient version of Django here. Don't expect anything very fancy
from django import newforms as forms

class BookmarksXMLImportForm(forms.Form):
    xml_field = forms.CharField(widget = forms.Textarea)


