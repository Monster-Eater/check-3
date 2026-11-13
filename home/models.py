from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.urls import reverse
from . validators import file_size
from ckeditor.fields import RichTextField





class Complaint(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="campus_complaints")
    attachment = models.FileField(upload_to="complaints/", null=True, blank=True)
    status = models.CharField(max_length=20, choices=[("open","Open"),("in_progress","In progress"),("resolved","Resolved")], default="open")
    name= models.CharField(max_length=120)
    email= models.CharField(max_length=100)
    phone= models.CharField(max_length=20)
    desc= models.TextField()
    date= models.DateField()
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('home')
    
#Create Meep Model
class Meep(models.Model):
    user = models.ForeignKey(User, related_name= "meeps",on_delete= models.DO_NOTHING)
    body = RichTextField(blank=True, null = True)
    # body = models.CharField(max_length=50000)
    created_at = models.DateTimeField(auto_now_add = True)
    likes = models.ManyToManyField(User, related_name = "meep_like", blank = True)
    category = models.CharField(max_length= 255, default='Entertainment')
    title = models.CharField(max_length=255, default = 'No Title')
    attachment = models.FileField(upload_to='feed_attachments/', blank=True, null=True)
    edited_at = models.DateTimeField(blank=True, null=True)
    client_id = models.UUIDField(blank=True, null=True, db_index=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','client_id'], condition=models.Q(client_id__isnull=False), name='unique_post_client_id')]

    def __str__(self):
        return self.title + ' | ' + str(self.user)


    def get_absolute_url (self):
        # return reverse('article-detail', args = (str(self.id)))
        return reverse('home')


    def number_of_likes(self):
        return self.likes.count()

    def __str__(self):
        return (
            f'{self.user}'
            f'({self.created_at:%Y-%m-%d %H:%M}):'
            f"{self.body}..."
            f"{self.title}"
            f"{self.category}"
           )

class Profile(models.Model):
    PRIVACY_CHOICES = [('everyone', 'Everyone'), ('followers', 'Followers'), ('nobody', 'Nobody')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField("self", 
    related_name = "followed_by",
    symmetrical= False, 
    blank=True)

    date_modified = models.DateTimeField(User, auto_now = True)
    profile_image = models.ImageField(null = True, blank = True, upload_to = 'profile-images/')
    profile_bio = models.CharField(null=True, blank=True, max_length=500)
    home_address = models.CharField(max_length=300, blank=True, default="")
    relationship_status = models.CharField(max_length=80, blank=True, default="")
    education_status = models.CharField(max_length=300, blank=True, default="")
    phone_number = models.CharField(max_length=32, blank=True, default="")
    phone_discoverable = models.BooleanField(default=False)
    homepage_link = models.CharField(null=True, blank=True, max_length=200)
    facebook_link = models.CharField(null=True, blank=True, max_length=200)
    instagram_link = models.CharField(null=True, blank=True, max_length=200)
    linkdin_link = models.CharField(null=True, blank=True, max_length=200)
    last_seen_privacy = models.CharField(max_length=16, choices=PRIVACY_CHOICES, default='everyone')
    status_privacy = models.CharField(max_length=16, choices=PRIVACY_CHOICES, default='everyone')
    read_receipts = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username



    
class Venue(models.Model):
    name = models.CharField('Venue Name', max_length=120)
    address = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    phone = models.CharField('Contact Phine', max_length=30, blank = True)
    web = models.URLField('Website Address', blank = True)
    email_address = models.EmailField('Email Address', blank = True)
    
    def __str__(self):
        return self.name
    
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user = instance)
        user_profile.save()
        user_profile.follows.set([instance.profile.id])
        user_profile.save()
post_save.connect(create_profile, sender = User)

class MyClubUser(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField('User Email')
    def __str__(self):
        return self.first_name + ' ' + self.last_name

class Event(models.Model):
    name= models.CharField('Event Name', max_length=120)
    event_date = models.DateTimeField('Event Date')
    venue = models.ForeignKey(Venue, blank=True, null = True, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, blank= True, null = True, on_delete=models.SET_NULL)
    description = models.TextField(blank = True)
    attendees = models.ManyToManyField(MyClubUser, blank = True)
    venue_image = models.ImageField(null=True, blank=True, upload_to = 'images/')
   

    def __str__(self):
        return self.name


class Video(models.Model):
    user = models.ForeignKey(User, related_name= "videos", on_delete= models.CASCADE)
    caption = models.CharField(max_length=300)
    video=models.FileField(upload_to="video/%y", validators=[file_size])
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.caption + ' | ' + str(self.user)
    def __str__(self):
        return (
            f'{self.user}'
            f'({self.created_at:%Y-%m-%d %H:%M}):'
            f"{self.video}..."
            f"{self.caption}"
           )
    
class Comment(models.Model):
    post = models.ForeignKey(Meep, related_name="comments", on_delete= models.CASCADE )    
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='social_comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    name = models.CharField(max_length= 255)
    body = models.TextField()
    date_added = models.DateField(auto_now_add= True)
    updated_at = models.DateTimeField(auto_now=True)


class PostReceipt(models.Model):
    post = models.ForeignKey(Meep, on_delete=models.CASCADE, related_name='receipts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_receipts')
    delivered_at = models.DateTimeField(blank=True, null=True)
    seen_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['post', 'user'], name='unique_post_receipt')]

    def __str__(self):
        return '%s - %s' % (self.post.title, self.name)
