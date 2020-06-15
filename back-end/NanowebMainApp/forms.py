from django import forms
from django.forms import widgets

from .models import Query

class QueryForm(forms.ModelForm):
    model = Query
    '''queryText = forms.CharField()
    queryText.widget.attrs.update({'class':'rounded_input_text','id':'id_text'})'''

    class Meta:
        model = Query
        fields = ['text']
        widgets= {'text': widgets.TextInput(attrs={'class':'rounded_input_text','id':'query','placeholder':'Lung carcinoma, Breast cancer...'})}
        labels = {'text':''}