from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import NUMBER_OF_POSTS
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .paginator import paginator


def index(request):
    template = 'posts/index.html'
    title = 'Последние записи'
    posts = Post.objects.select_related('author', 'group').all()
    page_number = request.GET.get('page')
    page_obj = paginator(posts, NUMBER_OF_POSTS, page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
        'index': True,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    title = 'Записи сообщества'
    posts = group.posts.select_related('author', 'group').all()
    page_number = request.GET.get('page')
    page_obj = paginator(posts, NUMBER_OF_POSTS, page_number)
    context = {
        'title': title,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    title = 'Профайл пользователя'
    template = 'posts/profile.html'
    following = False
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author', 'group').all()
    page_number = request.GET.get('page')
    page_obj = paginator(posts, NUMBER_OF_POSTS, page_number)
    post_counter = posts.count()
    if not isinstance(request.user, AnonymousUser):
        if Follow.objects.filter(user=request.user):
            following = True
    context = {
        'title': title,
        'author': author,
        'page_obj': page_obj,
        'post_counter': post_counter,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    posts = post.author.posts.select_related('author', 'group').all()
    post_counter = posts.count()
    comments = post.comments.all()
    context = {
        'post': post,
        'post_counter': post_counter,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None)
    is_edit = False
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user)
    context = {
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    redir_template = 'posts:post_detail'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect(redir_template, post_id=post_id)
    is_edit = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect(redir_template, post_id=post_id)
    context = {
        'form': form,
        'post': post,
        'is_edit': is_edit,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    redir_template = 'posts:post_detail'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(redir_template, post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    title = 'Избранные авторы'
    posts = Post.objects.select_related('author', 'group').filter(
        author__following__user=request.user,
    )
    page_number = request.GET.get('page')
    page_obj = paginator(posts, NUMBER_OF_POSTS, page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
        'following': True,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user_fol = Follow.objects.filter(user=request.user, author=author)
    if request.user != author and not user_fol.exists():
        Follow.objects.create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=author,
    ).delete()
    return redirect('posts:profile', author)
