from django import forms
from .models import UserDataFile,UserTable

class UserFileForm(forms.ModelForm):
    class Meta:
        model = UserDataFile
        fields = ['file']

class UserTableForm(forms.ModelForm):
    table_name = forms.CharField(max_length=255, required=True, help_text="Enter a unique table name")
    file = forms.ModelChoiceField(queryset=UserDataFile.objects.all(), required=True)

    class Meta:
        model = UserTable
        fields = ['file', 'table_name']