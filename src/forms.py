# -*- coding:utf-8 -*-

# This file is part of "My Own Delicious".
#
# "My Own Delicious" is free software: you can redistribute it and/or modify it
# under the terms of the Affero GNU General Public License as published by the
#  Free Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
# "My Own Delicious" is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
# FITNESS FOR A PARTICULAR PURPOSE.  See the Affero GNU General Public License 
# for more details.
#
# You should have received a copy of the Affero GNU General Public License along 
# with "My Own Delicious".  If not, see <http://www.gnu.org/licenses/>.


# We are using an ancient version of Django here. Don't expect anything very fancy
from django import newforms as forms

from xml.dom import minidom # import parse, parseString

class BookmarksXMLImportForm(forms.Form):
    """
    Very simple form, mostly here to easily validate handmade or pasted XML
    """
    xml_field = forms.CharField(label = 'Exported XML',
                                help_text = 'paste the XML you got from Delicious here',
                                required = True,
                                widget = forms.widgets.Textarea(attrs = {'rows':24, 'cols':80}))

