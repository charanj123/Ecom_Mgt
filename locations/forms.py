from django import forms
from .models import Location, StoreLocation


class LocationForm(forms.ModelForm):
    """Form for creating and updating locations."""
    class Meta:
        model = Location
        fields = ['name', 'address', 'city', 'state', 'country', 'zip_code', 'latitude', 'longitude']
        widgets = {
            'latitude': forms.NumberInput(attrs={'step': '0.000001', 'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'step': '0.000001', 'class': 'form-control'}),
        }


class StoreLocationForm(forms.ModelForm):
    """Form for creating and updating store locations."""
    class Meta:
        model = StoreLocation
        fields = ['name', 'address', 'city', 'state', 'country', 'zip_code', 
                 'latitude', 'longitude', 'phone_number', 'business_hours', 'is_active']
        widgets = {
            'latitude': forms.NumberInput(attrs={'step': '0.000001', 'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'step': '0.000001', 'class': 'form-control'}),
            'business_hours': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'is_active':
                field.widget.attrs.update({'class': 'form-control'})


class LocationSearchForm(forms.Form):
    """Form for searching locations by address or coordinates."""
    address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter address, city, or zip code'
        })
    )
    
    distance = forms.ChoiceField(
        choices=[
            ('10', 'Within 10 miles'),
            ('25', 'Within 25 miles'),
            ('50', 'Within 50 miles'),
            ('100', 'Within 100 miles'),
            ('250', 'Within 250 miles'),
        ],
        required=True,
        initial='25',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    latitude = forms.FloatField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    longitude = forms.FloatField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    def clean(self):
        cleaned_data = super().clean()
        address = cleaned_data.get('address')
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        
        if not address and not (latitude and longitude):
            raise forms.ValidationError(
                "Please provide either an address or coordinates for search."
            )
        
        return cleaned_data 