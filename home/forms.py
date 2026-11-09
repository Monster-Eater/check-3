from django import forms
from django.forms  import ModelForm
from .models import Venue, Event, Meep, Category, Video, Comment



class MeepForm(forms.ModelForm):
    body = forms.CharField(required=True,widget =forms.widgets.Textarea(attrs ={"placeholder" : "Enter Your Meep!", "class" : "form-control"} ),label="",)
    title = forms.CharField(required=True,label = '', widget =forms.widgets.TextInput (attrs ={"placeholder" : "Enter Meep-Title!", "class" : "form-control"} ),)
    category = forms.ChoiceField(choices=(), widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Query only when a form is requested, after database migrations have run.
        self.fields['category'].choices = list(
            Category.objects.order_by('name').values_list('name', 'name')
        )

    class Meta:
        model = Meep
        fields = ('body', 'title', 'category')
        exclude = ("user", "likes", )

    



#Create a venue form 
class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ('name', 'event_date', 'venue', 'manager', 'attendees', 'description', 'venue_image')

        labels = {   
            'name': '',
            'event_date':'YYYY-MM-DD',
            'venue':'Category',
            'manager':'Team Leader',
            'attendees':'Athurs',
            'description' :'',
            'venue_image' :'',
        }
        widgets = {
            'name': forms.TextInput(attrs= {'class': 'form-control', 'placeholder':'Article Name'}),
            'event_date':forms.TextInput(attrs= {'class': 'form-control', 'placeholder':'Date' }),
            'venue':forms.Select(attrs= {'class': 'form-select', 'placeholder':'Category' }),
            'manager':forms.Select(attrs= {'class': 'form-select', 'placeholder':'Team Leader'}),
            'attendees':forms.Select(attrs= {'class': 'form-select', 'placeholder':'Athurs'}),
            'description':forms.Textarea(attrs= {'class':'form-control', 'placeholder':'Description'}),
        }


class VenueForm(ModelForm):
    class Meta:
        model = Venue
        fields = ('name', 'address', 'zip_code', 'phone', 'web', 'email_address')

        labels = {   
            'name': '',
            'address':'',
            'zip_code':'',
            'phone':'',
            'web':'',
            'email_address':'',
            
        }
        widgets = {
            'name': forms.TextInput(attrs= {'class': 'form-control', 'placeholder':'Vneue Name'}),
            'address':forms.TextInput(attrs= {'class': 'form-control', 'placeholder':'Address' }),
            'zip_code':forms.TextInput(attrs= {'class': 'form-control', 'placeholder':'Zip Code' }),
            'phone':forms.TextInput(attrs= {'class': 'form-control', 'placeholder':'Contact Number'}),
            'web':forms.TextInput(attrs= {'class': 'form-control', 'placeholder':'Web Address'}),
            'email_address':forms.EmailInput(attrs= {'class':'form-control', 'placeholder':'Email Address'}),
        }



class Video_form(forms.ModelForm):
    class Meta:
        model=Video
        fields  = ('caption', 'video', 'user')
        labels = {   
            'caption': '',
            'video':'',
            
            
        }
        widgets = {
            'caption': forms.TextInput(attrs= {'class': 'form-control', 'placeholder':'Give a Title'}),
             'user' : forms.TextInput(attrs= {'class': 'form-control', 'value':'', 'id' : 'elder'}),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'body')
        widgets = {
            'name': forms.TextInput(attrs= {'class': 'form-control'}),
             'body' : forms.Textarea(attrs= {'class': 'form-control'}),
        }
