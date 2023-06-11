from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('all/', views.indexall, name="indexall"),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('p/<uuid:uuid>/', views.post_detail, name='post_detail'),
    path('load-more-posts/', views.load_more_posts, name='load_more_posts'),
    path('load-more-posts-follow/', views.load_more_posts_follow, name='load_more_posts_follow'),
    path('p/<uuid:uuid>/report/', views.report_post, name='report_post'),
    path('like/', views.like_post, name='like'),
    path('comment/<uuid:post_id>', views.add_comment, name='add_comment'),
    path('delete_comment/', views.delete_comment, name='delete_comment'),    path('follow', views.follow, name="follow"),
    path('forgot_password', views.forgot_password, name="forgot_password"),
    path('notifications', views.notifications, name='notifications'),
    path('delete_notification/<uuid:notification_id>/', views.delete_notification, name='delete_notification'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('profile/<str:pk>/more', views.profile_more, name='profile_more'),
    path('logout', views.logout, name='logout'),
    path('search', views.search, name='search'),
    path('upload', views.upload, name='upload'),
    path('settings', views.settings, name='settings'),
    path('search_results', views.search_results, name='search_results'),
    path('p/<uuid:uuid>/delete/', views.delete_post, name='delete_post'),
    path('p/<uuid:post_id>/verify/', views.verify_references, name='verify_references'),
    path('change_password/', views.change_password, name='change_password'),
    path('save_changes/<uuid:post_id>/', views.save_changes, name='save_changes'),

    path('reset_password/',auth_views.PasswordResetView.as_view(),name='reset_password'),
    path('reset_password_sent/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),



    
]

handler404 = 'app.views.error_404'