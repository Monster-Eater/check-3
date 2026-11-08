from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm 
from django.contrib.auth.models import User
from django import forms
from home.models import Profile


class ProfilePicForm(forms.ModelForm):
    profile_image = forms.ImageField(label = "Profile Picture")
    profile_bio = forms.CharField(label="Profile Bio", widget= forms.Textarea(attrs= {'class':'form-control', 'placeholder': 'Profile Bio'}))
    homepage_link = forms.CharField(label="", widget= forms.TextInput(attrs= {'class':'form-control', 'placeholder': 'Website Link'}))
    facebook_link = forms.CharField(label="", widget= forms.TextInput (attrs= {'class':'form-control', 'placeholder': 'Facebook Link'}))
    instagram_link = forms.CharField(label="", widget= forms.TextInput(attrs= {'class':'form-control', 'placeholder': 'Instagram Link'}))
    linkdin_link = forms.CharField(label="", widget= forms.TextInput(attrs= {'class':'form-control', 'placeholder': 'Linkdin Link'}))

    class Meta:
        model = Profile
        fields = ('profile_image', 'profile_bio', 'homepage_link', 'facebook_link', 'instagram_link', 'linkdin_link',)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label ='', widget= forms.EmailInput(attrs= {'class':'form-control', 'placeholder': 'Email Address'}))
    first_name = forms.CharField(label ='', max_length=30,widget= forms.TextInput(attrs= {'class':'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label ='', max_length=50,widget= forms.TextInput(attrs= {'class':'form-control', 'placeholder': 'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email','password1', 'password2')

    
    def __init__(self, *arg, **kwargs):
        super(SignUpForm, self).__init__(*arg, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label =''
        self.fields['username'].help_text = '<span class = "form-text text-muted"><small>Required. 150 character or fewer. Letters, digits and @/./+/-only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label =''
        self.fields['password1'].help_text = '<ul class= "form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters</li><li>Your password can\'t be a commonly used password</li><li>your password can\'t be entirely numeric</ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label =''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


class ChangePasswordFrom(SetPasswordForm):
	class Meta:
		model = User
		fields =  ['new_password1', 'new_password2']
		
	def __init__(self, *args, **kwargs):
		super(ChangePasswordFrom, self).__init__(*args, **kwargs)

		self.fields['new_password1'].widget.attrs['class'] = 'form-control'
		self.fields['new_password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['new_password1'].label = ''
		self.fields['new_password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['new_password2'].widget.attrs['class'] = 'form-control'
		self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['new_password2'].label = ''
		self.fields['new_password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'        	

class UpdateUserForm(UserChangeForm):
	password = None
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email')

	def __init__(self, *args, **kwargs):
		super(UpdateUserForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'User Name'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'
