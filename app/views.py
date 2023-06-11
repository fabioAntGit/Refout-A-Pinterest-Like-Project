from io import BytesIO
from django.core.files.images import ImageFile
import json
import uuid
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login
from django.contrib import messages
from itertools import chain
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from .models import Profile, Post, Referencia, LikePost, FollowersCount, Comment, Report, Notification, VerifyReferences
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.db import transaction
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.generic import RedirectView
from django.conf import settings
from PIL import Image
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str


# Create your views here.

@login_required
def error_404(request,exception):
    return render(request, '404.html')


@login_required
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=user_profile)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    posts = feed_list[:12]  # Retrieve only the first 12 posts

    return render(request, 'index2.html', {'user_profile': user_profile, 'posts': posts})

@login_required
def load_more_posts_follow(request):
    user_profile = request.user.profile
    limit = int(request.GET.get('limit', 24))
    offset = int(request.GET.get('offset', 0))

    following_profiles = FollowersCount.objects.filter(follower=user_profile).values_list('user', flat=True)
    posts = Post.objects.filter(user__in=following_profiles)[offset:offset + limit]  # Filter posts by the following profiles

    data = []
    for post in posts:
        data.append({
            'id': str(post.id),
            'image_url': post.image.url,
            'username': post.user.user.username
        })

    return JsonResponse(data, safe=False)





@login_required
def load_more_posts(request):
  user_object = User.objects.get(username=request.user.username)
  user_profile = Profile.objects.get(user=user_object)
  current_user_profile = request.user.profile
  limit = int(request.GET.get('limit', 24))
  offset = int(request.GET.get('offset', 0))

  posts = Post.objects.exclude(user=current_user_profile)[offset:offset + limit]

  data = []
  for post in posts:
    data.append({
      'id': str(post.id),
      'image_url': post.image.url,
      'username': post.user.user.username
    })

  return JsonResponse(data, safe=False)





@login_required
def indexall(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    current_user_profile = request.user.profile
    posts = Post.objects.exclude(user=current_user_profile)[:12]

    return render(request, 'indexall2.html', {'user_profile': user_profile, 'posts': posts})




# @login_required
# def like_post(request):
#     if request.POST.get('action') == 'post':
#         result = ''
#         id = request.POST.get('postid')
#         post = get_object_or_404(Post, id=uuid.UUID(id))
#         profile = get_object_or_404(Profile, user=request.user)
#         existing_noti = Notification.objects.filter(recipient=post.user,sender=request.user.profile,notification_type="like",post=post)
#         if post.likes.filter(id=profile.id).exists():
#             post.likes.remove(profile)
#             result = post.likes.count()
#             post.save()
#             if existing_noti.exists():
#                 existing_noti.delete()
        

#         else:
#             post.likes.add(profile)
#             result = post.likes.count()
#             post.save()
#             notifications = Notification.objects.create(recipient=post.user, sender=request.user.profile, notification_type="like", post=post)


#     return JsonResponse({'result': result})

from django.http import JsonResponse

@login_required
def like_post(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        result = ''
        post_id = request.POST.get('postid')
        post = get_object_or_404(Post, id=uuid.UUID(post_id))
        profile = get_object_or_404(Profile, user=request.user)

        if post.likes.filter(id=profile.id).exists():
            post.likes.remove(profile)
            result = post.likes.count()
        else:
            post.likes.add(profile)
            result = post.likes.count()

        return JsonResponse({'result': result})

    return JsonResponse({'error': 'Invalid request'})

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                

                #criação do profile

                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model)
                new_profile.save()
                return redirect('app:signin')
        else:
            messages.info(request, 'Password not matching')
            return redirect('app:signup')



            #criação do profile



    else:
        return render(request, 'signup2.html') 
    
@login_required
def logout(request):
    auth.logout(request)
    return redirect('signin?next=/')


@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        userauth = request.user
        
        user = User.objects.get(username=request.user.username)
        
        if user.check_password(old_password):
            if new_password == confirm_password:
                try:
                    validate_password(new_password, user=user)
                except ValidationError as error:
                    messages.error(request, error.messages[0])
                else:
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Your password was successfully updated!')
                    return redirect('app:profile', userauth)
            else:
                messages.error(request, 'New password and confirm password do not match.')
        else:
            messages.error(request, 'Invalid old password.')
    
    return render(request, 'registration/change_password.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid password or email')
    # Handle GET request or other cases
    return render(request, 'signin2.html')
    

def forgot_password(request):
    return render(request, 'password_reset_form.html')

@login_required
def notifications(request):
    user_profile = Profile.objects.get(user=request.user)
    notifications = Notification.objects.filter(recipient=user_profile)

    context = {
        'notifications':notifications,
        'user_profile':user_profile,
        
    }
    return render(request, 'notifications2.html', context)

@login_required
def delete_notification(request, notification_id):
    user_profile = Profile.objects.get(user=request.user)
    notifications = Notification.objects.filter(recipient=user_profile)

    for notification in notifications:
        if notification.id == notification_id:
            notification.delete()
            return JsonResponse({'status': 'ok'})


    return JsonResponse({'status': 'error'})


@login_required
def profile_more (request, pk):
    
    user_object=User.objects.get(username=pk)
    user_profile=Profile.objects.get(user=user_object)

    context = {
        'user_object':user_object,
        'user_profile':user_profile,
        
    }

    return render(request, 'profile_more2.html', context)


@login_required
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user = request.user
    

    
    # Get the list of users who are following the current account
    user_following_list = [following_count.user for following_count in FollowersCount.objects.filter(follower=user_profile)]
    
    # Get the list of users who are followers of the current account
    user_followers_list = FollowersCount.objects.filter(user=user_profile)

    user_object_visit = User.objects.get(username=pk)
    user_profile_visit = Profile.objects.get(user=user_object_visit)

    posts = Post.objects.filter(user=user_object.id)
    posts_no = Post.objects.filter(user=user_object.id).count()

    if user_profile_visit.user == request.user:
        # User is visiting their own profile, show Settings button
        text = 'Settings'
    else:
        # Check if the authenticated user is following the visited profile
        is_following = FollowersCount.objects.filter(follower=user.profile, user=user_profile_visit).exists()
        if is_following:
            text = 'Unfollow'
        else:
            text = 'Follow'

    
    user_followers = FollowersCount.objects.filter(user=user_profile).count()
    user_following = FollowersCount.objects.filter(follower=user_profile).count()

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'posts': posts,
        'posts_no': posts_no,
        'follower': user,
        'user': user_profile_visit,
        'admin': user,
        'text': text,
        'user_followers': user_followers,
        'user_following': user_following,
        'user_following_list': user_following_list,
        'user_followers_list': user_followers_list,
    }
    return render(request, 'profile2.html', context)


# @login_required
# def profile(request, pk):
#     user_object = User.objects.get(username=pk)
#     user_profile = Profile.objects.get(user=user_object)

#     user_object_visit = User.objects.get(username=pk)
#     user_profile_visit = Profile.objects.get(user=user_object_visit)

#     posts = Post.objects.filter(user=user_object.id)
#     posts_no = Post.objects.filter(user=user_object.id).count()

#     if FollowersCount.objects.filter(follower=request.user.profile, user=user_profile_visit).exists():
#         text = 'Unfollow'
#     else:
#         text = 'Follow'

#     user_followers = len(FollowersCount.objects.filter(user=user_profile_visit))
#     user_following = len(FollowersCount.objects.filter(follower=request.user.profile))

#     context = {
#         'user_object': user_object,
#         'user_profile': user_profile,
#         'posts': posts,
#         'posts_no': posts_no,
#         'follower': user_profile,
#         'user': user_profile_visit,
#         'text': text,
#         'user_followers': user_followers,
#         'user_following': user_following,
#     }
#     return render(request, 'profile.html', context)


def upload(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        image = request.FILES.get('image')
        description = request.POST['description']

        new_post = Post.objects.create(user=user_profile, image=image, description=description)

        categories = request.POST.getlist('category')
        descriptions = request.POST.getlist('descriptions')

        for i in range(len(categories)):
            category = categories[i]
            description = descriptions[i]
            new_ref = Referencia.objects.create(post=new_post, category=category, description=description)

        return redirect("/")
    else:
        return render(request, 'upload1.html', {'user_profile': user_profile})





# def upload(request):
#     user_object=User.objects.get(username=request.user.username)
#     user_profile=Profile.objects.get(user=user_object)
#     referencia=Referencia.objects.all()
#     if request.method == 'POST':
#         user = User.objects.get(username=request.user.username)
#         image = request.FILES.get('image')
#         description = request.POST['description']
#         new_post = Post.objects.create(user=user,image=image,description=description)
#         new_post.save()

#         category = request.POST.getlist('category[]')
#         descriptions = request.POST.getlist('descriptions[]')

#         for i in range(len(category)):
#             category = category[i]
#             descriptionss = descriptions[i]
#             new_ref = Referencia.objects.create(
#                 post= new_post,
#                 category=category,
#                 description=descriptionss,
#             )
#             new_ref.save()

#         return redirect("/")

#     else:   
#         return render(request, 'upload.html', {'user_profile': user_profile, 'referencia': referencia})
    
# @login_required
# def follow(request):
#     if request.method == 'POST':
#         follower = request.POST.get('follower')
#         user = request.POST.get('user')
        
#         if FollowersCount.objects.filter(follower=follower, user=user).first():
#             delete_follow = FollowersCount.objects.get(follower=follower, user=user)
#             delete_follow.delete()
#             return redirect('/profile/'+user)
#         else:
#             new_follower = FollowersCount.objects.create(follower = follower, user = user)
#             new_follower.save()
#             return redirect('/profile/'+user)
        
#     else:
#         return redirect('profile', pk=user.user.username)

@login_required
def follow(request):
    if request.method == 'POST':
        
        follower_id = request.POST.get('follower')
        user_id = request.POST.get('user')
        userurl = request.POST.get('userurl')
        follower = Profile.objects.get(id=follower_id)
        user = Profile.objects.get(id=user_id)
        existing_noti = Notification.objects.filter(recipient=user,sender=follower,notification_type="follow")

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follow = FollowersCount.objects.get(follower=follower, user=user)
            delete_follow.delete()
            if existing_noti.exists():
                existing_noti.delete()

            return redirect('/profile/'+userurl)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            Notification.objects.create(recipient=user,sender=follower,notification_type="follow")
            return redirect('/profile/'+userurl)
        
    else:
        return redirect('profile', pk=user.user.username)



    

@login_required
def search(request):
    user_profile = Profile.objects.get(user=request.user)
    return render(request, 'search2.html', {'user_profile': user_profile})

@login_required
def search_results(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        user = request.POST.get('user')
        qs = Profile.objects.filter(user__username__icontains=user)

        if len(qs) > 0 and len(user) > 0:
            data = []
            for pos in qs:
                item = {
                    'username': pos.user.username,
                    'image': pos.profile_picture.url,
                }
                data.append(item)
            return JsonResponse({'data': json.dumps(data)})
        else:
            return JsonResponse({'data': 'no users found...'})
    return JsonResponse({})

@login_required
def post(request):
    # if request.method == 'POST':
    #     post_id = request.POST.get('postid')
    #     post = Post.objects.get(id=post_id)
    #     comment = Comment.objects.get(post=post_id)
    #     likes_count = post.likes.count()
    #     data = {
    #         'image': post.image.url,
    #         'user': post.user.user.username,
    #         'created': post.created.strftime("%d/%m/%Y at %H:%M"),
    #         'likes': likes_count,
    #         'profile_picture': post.user.profile_picture.url,
            
    #     }
    #     return JsonResponse(data)
    # else:
        return render(request, 'post.html')

@login_required
def post_detail(request, uuid):
    post = get_object_or_404(Post, id=uuid)
    user_profile = Profile.objects.get(user=request.user)
    comments = Comment.objects.filter(post=post).order_by('-created')
    referencias = post.referencias.all()  # get all references related to the post
    context = {
        'post': post,
        'comments': comments,
        'referencias': referencias,
        'user_profile': user_profile
    }
    return render(request, 'post2.html', context)

@login_required
def save_changes(request, post_id):
    if request.method == 'POST':
        # Retrieve the updated data from the form
        descriptionpost = request.POST.get('description')

        # Get the category and description of related references
        references = Referencia.objects.filter(post_id=post_id)
        updated_references = []
        for referencia in references:
            category = request.POST.get(f'category{referencia.id}')
            description = request.POST.get(f'description{referencia.id}')
            updated_references.append((category, description))

        # Update the post and references in the database
        post = Post.objects.get(id=post_id)
        post.description = descriptionpost
        post.save()

        for i, referencia in enumerate(references):
            referencia.category = updated_references[i][0]
            referencia.description = updated_references[i][1]
            referencia.save()

        # Redirect back to the post detail page
        return redirect(reverse('app:post_detail', kwargs={'uuid': post_id}))

@login_required
def delete_reference(request):
    if request.method == 'POST':
        reference_id = request.POST.get('reference_id')
        delete_reference = request.POST.get('delete_reference')
        
        if delete_reference == '1':
            # Perform the deletion of the reference from the database
            try:
                reference = Referencia.objects.get(id=reference_id)
                reference.delete()
                return JsonResponse({'success': True})
            except Referencia.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Reference does not exist'})
        else:
            return JsonResponse({'success': False, 'error': 'Deletion not confirmed'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        text = request.POST.get('text')

        if text:
            comment = Comment.objects.create(user=request.user.profile, post=post, text=text)
            
            if request.user != post.user.user:  # Check if the commenting user is not the post owner
                # Create a notification
                notification = Notification.objects.create(
                    recipient=post.user,
                    sender=request.user.profile,
                    notification_type='comment',
                    post=post,
                    comment=comment  # Associate the comment with the notification
                )
            
            return JsonResponse({
                'user': comment.user.user.username,
                'text': comment.text,
                'post_user': post.user.user.username,
                'comment_id': comment.id
            })
        
        return HttpResponseBadRequest("Invalid comment text")
    
    return HttpResponseBadRequest("Invalid request method")





@login_required
def settings(request):
    
    user = request.user
    user_profile = Profile.objects.get(user=user)

    if request.method == 'POST':
        username = request.POST.get('username', '')  # Retrieve the value of 'username'
        email = request.POST.get('email', '')

        if User.objects.exclude(pk=user.pk).filter(username=username).exists():
            messages.error(request, 'This username is already taken.')
            
            if User.objects.exclude(pk=user.pk).filter(email=email).exists():
                messages.error(request, 'This Email is already taken.')
                return redirect('app:settings')
            else:
                user.email = email
                return redirect('app:settings')
        else:
            user.username = username
            if User.objects.exclude(pk=user.pk).filter(email=email).exists():
                messages.error(request, 'This Email is already taken.')
                return redirect('app:settings')
            else:
                user.email = email
                
            

        

        user_profile.first_name = request.POST['first_name']
        user_profile.last_name = request.POST['last_name']
        user_profile.bio = request.POST['bio']
        user_profile.country = request.POST['country']
        image_file = request.FILES.get('image')
        banner_image_file = request.FILES.get('banner_image')

        # Update the profile picture and banner image if they exist
        if image_file:
            user_profile.profile_picture.save(image_file.name, image_file)
        if banner_image_file:
            user_profile.profile_banner.save(banner_image_file.name, banner_image_file)
        
        user.save()
        user_profile.save()
        messages.success(request, 'Your settings have been saved.')
        return redirect('app:settings')
    
    context = {
        'user_profile': user_profile,
        'user': user,
        
    }
    return render(request, 'settings2.html', context)


def verify_references(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    referer = request.META.get('HTTP_REFERER')
    
    if request.method == 'POST':
        # Create a new VerifyReferences object
        verify_references = VerifyReferences.objects.create(post=post)

        # Get all the references related to the post
        references = Referencia.objects.filter(post=post)

        # Add the references to the VerifyReferences object
        verify_references.references.set(references)

        if referer:
            return HttpResponseRedirect(referer)
        else:   
            return redirect('app:post_detail', user)

    return render(request, 'app:verify_references', {'post': post})

@login_required
def report_post(request, uuid):
    post = get_object_or_404(Post, id=uuid)
    if request.method == 'POST':
        category = request.POST.get('category')
        if category:    
            try:
                report = Report.objects.get(post=post, category=category)
                if not report.reported.filter(id=request.user.profile.id).exists():
                    report.reported.add(request.user.profile)
                    report.save()
                messages.success(request, 'Reported successfully.')
            except Report.DoesNotExist:
                report = Report.objects.create(post=post, category=category)
                report.reported.add(request.user.profile)
                report.save()
                messages.success(request, 'Reported successfully.')
        return redirect('app:post_detail', uuid=post.id)

    else:
        context = {
            'post': post,
            'categories': Report.CATEGORY_CHOICES,
        }
        return render(request, 'post2.html', context)

def delete_comment(request):
    if request.method == 'POST' and request.user.is_authenticated:
        comment_id = request.POST.get('comment_id')
        try:
            comment = Comment.objects.get(id=comment_id, user=request.user.profile)
            comment.delete()
            return JsonResponse({'success': True})
        except Comment.DoesNotExist:
            pass
    
    return JsonResponse({'success': False})

def delete_comment(request):
    if request.method == 'POST' and request.user.is_authenticated:
        comment_id = request.POST.get('comment_id')
        try:
            comment = Comment.objects.get(id=comment_id, user=request.user.profile)
            # Check for associated notifications and delete them
            Notification.objects.filter(comment=comment).delete()
            comment.delete()
            return JsonResponse({'success': True})
        except Comment.DoesNotExist:
            pass
    
    return JsonResponse({'success': False})


@login_required
def delete_post(request, uuid):
    post = get_object_or_404(Post, id=uuid)
    user = request.user
    if request.method == 'POST':
        post.delete()
        return redirect('app:profile', user)

    return render(request, 'app:delete_post', {'post': post})


def password_reset(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('reset_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(mail_subject, message, 'refoutapp@gmail.com', [email])
            return redirect('app:signin')
        except User.DoesNotExist:
            pass
    return render(request, 'forgot_password.html')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            # Token is valid, allow the user to set a new password
            if request.method == 'POST':
                password = request.POST['password']
                user.set_password(password)
                user.save()
                return redirect('password_reset_complete')
            return render(request, 'password_reset_confirm.html')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass
    return redirect('password_reset_invalid')