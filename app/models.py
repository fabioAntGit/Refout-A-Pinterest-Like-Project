import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import uuid
from PIL import Image
# from django_countries.fields import CountryField

class Profile(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    profile_picture= models.ImageField(default='blank-profile-picture.jpg', upload_to='profile_pictures/')
    profile_banner= models.ImageField(default='blank-banner-picture.jpg', upload_to='profile_pictures/')
    bio = models.TextField(blank=True)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.profile_picture:
            profile_path = self.profile_picture.path

            # Open the image using Pillow
            img2 = Image.open(profile_path)

            width_profile = 200
            height_profile = 200
            resized_profile_img = img2.resize((width_profile, height_profile), resample=Image.NEAREST)


            # Save the resized image, overwriting the original file
            resized_profile_img.save(profile_path)

        if self.profile_banner:
            banner_path = self.profile_banner.path

            # Open the image using Pillow
            img = Image.open(banner_path)

            width_banner = 1546
            height_banner = 423
            resized_banner_img = img.resize((width_banner, height_banner), resample=Image.NEAREST)

            # Save the resized image, overwriting the original file
            resized_banner_img.save(banner_path)


    def get_posts_no (self):
        return self.posts.all().count()
    
    def get_all_posts (self):
        return self.posts.all()
    
    def get_likes_given_no (self):
        likes = self.like_set.all()
        total_liked = 0
        for item in likes:
            if item.value == 'Like':
                total_liked += 1
        return total_liked
    
    
    def get_likes_recieved_no(self):
        posts = self.posts.all()
        total_liked = 0
        for item in posts:
            total_liked+= item.likes.all().count()
        return total_liked

    class Meta:
        db_table='profile' 

    def __str__(self):
        return str(self.user.username)
    
    
class Post(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")
    description = models.TextField(null=True)
    image = models.ImageField(blank=True, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])], upload_to='post_images/')
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(Profile, blank=True, related_name='likes')  
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            image_path = self.image.path

            # Open the image using Pillow
            img = Image.open(image_path)

            # Resize the image to 450x700 pixels without maintaining the aspect ratio
            width = 450
            height = 700
            resized_img = img.resize((width, height), resample=Image.NEAREST)

            # Save the resized image, overwriting the original file
            resized_img.save(image_path)

    def num_likes(self):
        return self.likes.all().count()

    def num_comments(self):
        return self.comment_set.all().count()

    def __str__(self):
        return str(self.user)

class Comment(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()


    class Meta:
        db_table='comment' 

    def __str__(self):
        return '%s - %s' % (self.user, self.text)

class Referencia(models.Model):
    CATEGORY_CHOICES = (
        ('pants', 'Pants'),
        ('t_shirt', 'T-Shirt'),
        ('jacket', 'Jacket'),
        ('hat', 'Hat'),
        ('shorts', 'Shorts'),
        ('shirt', 'Shirt'),
        ('belt', 'Belt'),
        ('shoes', 'Shoes'),
        ('watch', 'Watch'),
        ('necklace', 'Necklace'),
        ('ring', 'Ring'),
        ('earring', 'Earring'),
        ('bag', 'Bag'),
    )

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='referencias')
    description = models.TextField(null=True)
    category = models.CharField(max_length=8, choices=CATEGORY_CHOICES, null=True)
    link = models.URLField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'referencia'

    def __str__(self):
        return self.description
    
    
class VerifyReferences(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='verify_references')
    references = models.ManyToManyField(Referencia, blank=True, related_name='verify_references')
    as_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'verify_references'

    def __str__(self):
        return f"VerifyReferences for post: {self.post.id}"

    
class LikePost (models.Model):
    LIKE_CHOICES=(
        ('Like', 'Like'),
        ('Unlike', 'Unlike'),
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_like')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user_like')
    value = models.CharField(choices=LIKE_CHOICES, max_length=8)


    class Meta:
        db_table='likepost' 
    
    def __str__(self):
        return f"{self.user}-{self.post}-{self.value}"

    
    
class FollowersCount(models.Model):
    follower = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="follower")
    user=  models.ForeignKey(Profile, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('-created',)
    
    def __str__(self) -> str:
        return '{} follows {}'.format(self.follower, self.user)


class Notification(models.Model):
    NOTIFICATION_TYPE = (('like', 'liked your post'), ('comment', 'Commented on your post'), ('follow', 'Started following you'))

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    recipient = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="recipient")
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="sender")
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    comment= models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True)
    read = models.BooleanField(default=False)


class Report(models.Model):
    CATEGORY_CHOICES = (
        ( 'no_references','there are no references / Incorrect references'),
        ('inappropriate', 'Inappropriate content'),
        

    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='report_post', blank=True, null=True)
    reported = models.ManyToManyField(Profile, blank=True, related_name='reported')  
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return 'Report: ({}) {}'.format(self.category, self.post)
