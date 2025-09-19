from django import forms
from .models import Product, ProductImage, ProductRating


class ProductForm(forms.ModelForm):
    """Form for creating and editing products."""
    class Meta:
        model = Product
        fields = [
            'title', 'description', 'price', 'discount_price',
            'category', 'product_type', 'condition', 'brand',
            'quantity', 'latitude', 'longitude', 'address', 'city', 'state',
            'country', 'zip_code'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['price'].widget.attrs.update({'class': 'form-control'})
        self.fields['discount_price'].widget.attrs.update({'class': 'form-control'})
        self.fields['category'].widget.attrs.update({'class': 'form-select'})
        self.fields['product_type'].widget.attrs.update({'class': 'form-select'})
        self.fields['condition'].widget.attrs.update({'class': 'form-select'})
        self.fields['brand'].widget.attrs.update({'class': 'form-control'})
        self.fields['quantity'].widget.attrs.update({'class': 'form-control'})
        self.fields['address'].widget.attrs.update({'class': 'form-control'})
        self.fields['city'].widget.attrs.update({'class': 'form-control'})
        self.fields['state'].widget.attrs.update({'class': 'form-control'})
        self.fields['country'].widget.attrs.update({'class': 'form-control'})
        self.fields['zip_code'].widget.attrs.update({'class': 'form-control'})


class ProductImageForm(forms.ModelForm):
    """Form for uploading product images."""
    class Meta:
        model = ProductImage
        fields = ['image', 'is_main', 'alt_text']
        widgets = {
            'alt_text': forms.TextInput(attrs={'class': 'form-control'}),
        }


ProductImageFormSet = forms.inlineformset_factory(
    Product, ProductImage, form=ProductImageForm,
    extra=3, can_delete=True
)


class ProductRatingForm(forms.ModelForm):
    """Form for rating products."""
    class Meta:
        model = ProductRating
        fields = ['rating', 'review']
        widgets = {
            'review': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'rating': forms.RadioSelect()
        }


class ProductFilterForm(forms.Form):
    """Form for filtering products in search results."""
    PRICE_CHOICES = (
        ('', 'Any Price'),
        ('0-50', 'Under $50'),
        ('50-100', '$50 to $100'),
        ('100-200', '$100 to $200'),
        ('200-500', '$200 to $500'),
        ('500-1000', '$500 to $1000'),
        ('1000-10000', 'Over $1000'),
    )
    
    SORT_CHOICES = (
        ('created_at', 'Newest First'),
        ('-created_at', 'Oldest First'),
        ('price', 'Price Low to High'),
        ('-price', 'Price High to Low'),
        ('-views', 'Most Popular'),
    )
    
    category = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    product_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Product.TYPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    condition = forms.ChoiceField(
        choices=[('', 'Any Condition')] + list(Product.CONDITION_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    price_range = forms.ChoiceField(
        choices=PRICE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='created_at',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, State, or Zip'})
    )
    
    distance = forms.ChoiceField(
        choices=[
            ('', 'Any Distance'),
            ('10', 'Within 10 miles'),
            ('25', 'Within 25 miles'),
            ('50', 'Within 50 miles'),
            ('100', 'Within 100 miles'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        from .models import Category
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all() 