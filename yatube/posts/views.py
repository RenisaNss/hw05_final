from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm, CommentForm
from .models import Post, Group, Follow
from django.core.paginator import Paginator


User = get_user_model()
NUM = 10


def paginator(request, value):
    paginator = Paginator(value, NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    post_list = Post.objects.all()
    page_obj = paginator(request, post_list)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
        'index': True
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    page_obj = paginator(request, posts)
    template = 'posts/group_list.html'
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = (
        request.user.is_authenticated and Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    )
    posts = author.posts.all()
    page_obj = paginator(request, posts)
    context = {
        'following': following,
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'post_id': post_id,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def add_comment(request, post_id):
    """Save comment in DB."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post_id = post.id
        comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(
            request.POST,
            files=request.FILES or None,
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user)
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    post.delete()
    return redirect('posts:index')


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id,
    }
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', context)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(request, posts)
    # Добавил проверку на то подписан ли юзер хотя бы на одного пользователя
    # что бы в случае False, отобразить пользователю сообщение об этом,
    # и предложить перейти на главную
    existence_of_subscription = Follow.objects.filter(
        user=request.user
    ).exists()
    context = {
        'page_obj': page_obj,
        'follow': True,
        'existence_of_subscription': existence_of_subscription
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора"""
    author = get_object_or_404(User, username=username)
    check_for_existence = (
        Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    )
    if not check_for_existence and author != request.user:
        Follow.objects.create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    """Дизлайк, отписка"""
    author = get_object_or_404(User, username=username)
    # Андрей Никулин, все что ниже в комментарии верно?
    # Лучше сделать отписку через filter(..).delete(),
    # тогда не потребуется предварительная проверка наличия объекта
    # в БД и количество запросов уменьшиться с 3 до 1.
    # Ошибки при ненахождении не будет, пользователь останется
    # на той же странице что и был, ничего не произойдет.
    Follow.objects.filter(
        user=request.user,
        author=author
    ).delete()
    return redirect('posts:profile', username)
