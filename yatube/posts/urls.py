from django.urls import path

from . import views

app_name = 'posts'



# При обращении к какому-нибудь URL Django-проекта запрос передаётся в urls.py, и там специальный обработчик path() вызывает view-объект(ф-цию или класс), передавая ему в качестве аргумента объект типа request, а на выходе ожидает объект типа response. Объекты response могут быть созданы встроенными функциями-помощниками, например, функцией render() (создаются в обработчике)

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('delete/<int:post_id>/', views.post_delete, name='post_delete'),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow, 
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ), 
]
