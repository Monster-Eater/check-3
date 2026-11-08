from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from django.http import HttpResponseRedirect
from .models import Event, Profile, Meep, Complaint, Donate, Category, Video, Comment
from.forms import VenueForm, EventForm, MeepForm, Video_form, CommentForm
from django.contrib import messages
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import  train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from django.views.generic import CreateView, DetailView, ListView
from django.contrib.auth.models import User
from django.urls import reverse_lazy





#=================== Home =========================
def vant(request):
    return render(request,'home/vant.html')


def video(request):
    all_video=Video.objects.all().order_by("-created_at")
    if request.method == "POST":
        form=Video_form(data=request.POST, files= request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Uploaded Successfully....!")
            return redirect('home') 
    else:
        form = Video_form()    
    return render (request, 'home/video.html', {"form": form, 'all_video': all_video})

# def ownvideo(request,pk):
#     if request.user.is_authenticated:    
#         if request.user.id == pk:
#            video = Video.objects.all()
#            form=Video_form(data=request.POST, files= request.FILES)    
#         return render (request, 'home/ownvideo.html', {'video': video, 'form' : form})
#     else:
#         messages.success(request, 'Your must be logged in to view this page....!')
#         return redirect('home')
    


def complaint(request):
    if request.method =="POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc = request.POST.get('desc')
        complain = Complaint(name=name, email=email, phone=phone, desc=desc, date = datetime.today())
        complain.save()
        messages.success(request, 'Your Complain Has Been Submitted and Sended To Chairman Successfully.Thanks....!')
        return redirect('complaint')
    return render(request, 'home/complaint.html')


def profile(request, pk):
    if request.user.is_authenticated:        
        profile = Profile.objects.get(user_id = pk)
        meeps = Meep.objects.filter(user_id = pk).order_by("-created_at")
        # videos = Video.objects.get(video).order_by("-created_at")
        if request.method =='POST':
            current_user_profile = request.user.profile
            action = request.POST['follow']
            if action == "unfollow":
                current_user_profile.follows.remove(profile)
            elif action == "follow":
                current_user_profile.follows.add(profile)
            current_user_profile.save()    
        return render (request, "home/profile.html", {
            "profile": profile,
            'meeps': meeps,
            # 'viedos': videos,
        })
    else:
        messages.success(request, 'Your must be logged in to view this page....!')
        return redirect('home')

def followers(request, pk):
    if request.user.is_authenticated:
        if request.user.id == pk:
           profiles = Profile.objects.get(user_id=pk)
           return render (request, 'home/followers.html', {"profiles": profiles,})
        else:
            messages.success(request, "That's Not Your Profile Page....!")
        return redirect('home')    
    else:
        messages.success(request, 'You Must Be Logged In To Do That....!')
        return redirect('home')

def follows(request, pk):
    if request.user.is_authenticated:
        if request.user.id == pk:
           profiles = Profile.objects.get(user_id=pk)
           return render (request, 'home/follows.html', {"profiles": profiles,})
        else:
            messages.success(request, "That's Not Your Profile Page....!")
        return redirect('home')    
    else:
        messages.success(request, 'You Must Be Logged In To Do That....!')
        return redirect('home')   

def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user = request.user)
        return render (request, 'home/profile_list.html', {
        "profiles": profiles,})
    else:
        messages.success(request, ("Sorry...! You Must Be Logged In"))
        return redirect('home')

def unfollow(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        request.user.profile.follows.remove(profile)
        request.user.profile.save()
        messages.success(request, (f"You Have Successfully Unfollowed {profile.user.username}...!"))
        return redirect(request.META.get("HTTP_REFERER")) 
    else:
        messages.success(request, 'You Must Be Logged In To Do That....!')
        return redirect('home')
def follow(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        request.user.profile.follows.add(profile)
        request.user.profile.save()
        messages.success(request, (f"You Have Successfully Followed {profile.user.username}...!"))
        return redirect(request.META.get("HTTP_REFERER")) 
    else:
        messages.success(request, 'You Must Be Logged In To Do That....!')
        return redirect('home')

def home(request):
    if request.user.is_authenticated:
        form = MeepForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                meep = form.save(commit= False)
                meep.user = request.user
                meep.save()
                messages.success(request, 'Your Meep Has Been Posted....!')
                return redirect("home")            
        meeps = Meep.objects.all().order_by("-created_at")
        return render (request, 'home/home.html', {'meeps': meeps, 'form': form})
    else:
        meeps = Meep.objects.all().order_by("-created_at")
        return render (request, 'home/home.html', {'meeps': meeps })

class MeepDetailView(DetailView):
    model = Meep
    template_name = 'home/meep_detail.html'
    fields = '__all__'

def meep_show(request, pk):
    meep = get_object_or_404(Meep, id=pk)
    if meep:
        return render(request, "home/meep_show.html", {'meep':meep})
    else:
        messages.success(request, 'That Meep Does Not Exist....!')
        return redirect('home')    

def CategoryView(request, cats):
    category_meeps = Meep.objects.filter(category=cats)
    return render(request, 'home/categories.html', {'cats': cats.title(), 'category_meeps':category_meeps})


class AddCommentView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'home/add_comment.html'
    def form_valid(self, form):
        form.instance.post_id = self.kwargs['pk']
        return super().form_valid(form)
       
    success_url = reverse_lazy('home')


def delete_meep(request, pk):
    if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id=pk)
        # check to see if you on the maap
        if request.user.username == meep.user.username:
            meep.delete()
            messages.success(request, "The Meep Has Been Deleted....!")
            return redirect(request.META.get("HTTP_REFERER")) 
        else:
            messages.success(request, "You Don't Own That Meep....!")
            return redirect(request.META.get("HTTP_REFERER")) 
    else:
        messages.success(request, 'Please Login To Continue....!')
        return redirect("home")  

def edit_meep(request,pk):
    if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id=pk)
        if request.user.username == meep.user.username:
            
            form = MeepForm(request.POST or None, instance=meep)
            if request.method == "POST":
                if form.is_valid():
                    meep = form.save(commit= False)
                    meep.user = request.user
                    meep.save()
                    messages.success(request, 'Your Meep Has Been Updated....!')
                    return redirect("home")        
            else:
                return render (request, 'home/edit_meep.html', {"form": form, 'meep' : meep})
                return redirect(request.META.get("HTTP_REFERER")) 
        else:
            messages.success(request, "You Don't Own That Meep....!")
            return redirect('home') 
    else:
        messages.success(request, 'Please Login To Continue....!')
        return redirect("home")  

def search(request):
    if request.method == 'POST':
        search = request.POST['search']
        searched = Meep.objects.filter(body__contains = search) 

        return render(request, 'home/search.html', {'search': search, 'searched': searched,})

    else:
        return render(request, 'home/search.html', {})

def search_user(request):
    if request.method == 'POST':
        search = request.POST['search']
        searched = User.objects.filter(username__contains = search) 

        return render(request, 'home/search_user.html', {'search': search, 'searched': searched,})

    else:
        return render(request, 'home/search_user.html', {})

class AddCategoryView(CreateView):
    model = Category
    #form_class = PostForm
    template_name = 'home/add_category.html'
    fields = '__all__'

def add_event(request):
    submitted = False
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/add_event?submitted=True') 
    else:
      
        form = EventForm
        if "submitted" in request.GET:
            submitted= True
    return render (request, 'home/add_event.html', {
        "form": form,
        "submitted": submitted,
    })

    #===================================Tools========================================

def bmi(request):
    return render(request, 'home/bmi.html')
def donate(request):
    if request.method =="POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc = request.POST.get('desc')
        donate = Donate(name=name, email=email, phone=phone, desc=desc, date = datetime.today())
        donate.save()
    return render(request, 'home/donate.html')

def predict(request):
    return render(request, 'home/predict.html')
def result(request):
    data = pd.read_csv(r"/home/husnain/Public/Web development/DJango/Projects/diabetes/static/diabetes.csv")
    x = data.drop("Outcome", axis=1)
    y = data["Outcome"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)
    model = LogisticRegression()
    model.fit(x_train, y_train)
    val1=float(request.GET['n1'])
    val2 = float(request.GET['n2'])
    val3 = float(request.GET['n3'])
    val4 = float(request.GET['n4'])
    val5 = float(request.GET['n5'])
    val6 = float(request.GET['n6'])
    val7 = float(request.GET['n7'])
    val8 = float(request.GET['n8'])
    pred=model.predict([[val1,val2,val3,val4,val5,val6,val7,val8]])
    result1=""
    if pred==[1]:
        result1="Positive"
    else:
        result1="Negetive"
    return render(request, 'home/predict.html',{"result2":result1})


def add_venue(request):
    submitted = False
    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/add_venue?submitted=True') 
    else:
      
        form = VenueForm
        if "submitted" in request.GET:
            submitted= True
    return render (request, 'home/add_venue.html', {
        "form": form,
        "submitted": submitted,
    })



def all_events(request):
   event_list = Event.objects.all()
   return render(request, 'home/event_list.html', {
       'event_list': event_list,
   })



def campus(request, year= datetime.now().year, month= datetime.now().strftime('%B')):
    name = 'Sallam'
    month = month.capitalize()
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)

    cal = HTMLCalendar().formatmonth(
        year,
        month_number)
    now = datetime.now()
    current_year = now.year

    time = now.strftime('%I:%M %p ')
    return render (request, 'home/campus.html' , {
        'name': name,
        'year': year,
        'month': month,
        'month_number': month_number,
         'cal': cal, 
         'current_year': current_year,  
         'time':time,
})

def meep_like(request, pk):
    if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id= pk)
        if meep.likes.filter(id= request.user.id):
           meep.likes.remove(request.user)
        else:
            meep.likes.add(request.user)
        
        return redirect(request.META.get("HTTP_REFERER"))    
    else:
        messages.success(request, ('Sorry! You must be logged in to like this meep....!'))
        return redirect('home')


#===================   Diciplenes   ========================

def rehb(request):
    return render (request, "diciplen/rehb.html", {})
def applied(request):
    return render (request, "diciplen/applied.html", {})
def comp(request):
    return render (request, "diciplen/comp.html", {})
def engin(request):
    return render (request, "diciplen/engin.html", {})
def islamic_study(request):
    return render (request, "diciplen/islamic_study.html", {})
def phsyco(request):
    return render (request, "diciplen/phsyco.html", {})
def chemis(request):
    return render (request, "diciplen/chemis.html", {})
def socio(request):
    return render (request, "diciplen/socio.html", {})



#======================  Departments  =====================

def biotech(request):
    return render (request, "departments/biotech.html", {})
def hnd(request):
    return render (request, "departments/hnd.html", {})
def mlt(request):
    return render (request, "departments/mlt.html", {})
def dpt(request):
    return render (request, "departments/dpt.html", {})
def slp(request):
    return render (request, "departments/slp.html", {})
def mit(request):
    return render (request, "departments/mit.html", {})
def food_science(request):
    return render (request, "departments/food_science.html", {})
def botany(request):
    return render (request, "departments/botany.html", {})
def softeng(request):
    return render (request, "departments/softeng.html", {})
def infotech(request):
    return render (request, "departments/infotech.html", {})
def datascience(request):
    return render (request, "departments/datascience.html", {})
def cybersec(request):
    return render (request, "departments/cybersec.html", {})
def computersci(request):
    return render (request, "departments/computersci.html", {})
def electricalengin(request):
    return render (request, "departments/electricalengin.html", {})
def bioinformatics(request):
    return render (request, "departments/bioinformatics.html", {})
def phsycodiploma(request):
    return render (request, "departments/phsycodiploma.html", {})
def appliedphsyco(request):
    return render (request, "departments/appliedphsyco.html", {})
def chemistry(request):
    return render (request, "departments/chemistry.html", {})
def biochem(request):
    return render (request, "departments/biochem.html", {})
def criminology(request):
    return render (request, "departments/criminology.html", {})
def masscomm(request):
    return render (request, "departments/masscomm.html", {})
def mediasci(request):
    return render (request, "departments/mediasci.html", {})
def sociology(request):
    return render (request, "departments/sociology.html", {})
