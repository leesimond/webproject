from django import forms
from bestmenu.models import Restaurant, Category, UserProfile
from django.forms.widgets import TextInput
from django.contrib.auth.models import User

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        # Provide an association between the ModelForm and a model
        model = Category
        fields = ('name',)


class RestaurantForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Please enter the name of the Restaurant.")
    url = forms.URLField(max_length=200, help_text="Please enter the URL of the restaurant.", initial="http://", widget=TextInput)
    #views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        # Provide an association between the ModelForm and a model
        model = Restaurant
        exclude = ('category', 'likes', 'views')

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        # If url is not empty and doesn't start with 'http://', prepend 'http://'.
        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url

        return cleaned_data

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    website = forms.URLField(max_length=200, help_text="Please enter the URL of your website", initial="http://", widget=TextInput, required=False)
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')
    
    def clean(self):
        cleaned_data = self.cleaned_data
        website = cleaned_data.get('website')

        if website and not website.startswith('http://'):
            website = 'http://' + website
            cleaned_data['website'] = website
        
        return cleaned_data

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')
    
    def clean(self):
        cleaned_data = self.cleaned_data
        website = cleaned_data.get('website')

        if website and not website.startswith('http://'):
            website = 'http://' + website
            cleaned_data['website'] = website
        
        return cleaned_data
