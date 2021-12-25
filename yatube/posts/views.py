from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow

POSTS_COUNT = 15
CACHE_TIME = 20  # sec


def get_page_obj(request, posts):
    paginator = Paginator(posts, POSTS_COUNT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(CACHE_TIME)
def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': get_page_obj(request, Post.objects.all()),
    })


# @cache_page(CACHE_TIME)
@login_required
def follow_index(request):
    return render(request, 'posts/follow.html', {
        'page_obj': get_page_obj(request, Post.objects.filter(
            author__following__user=request.user))
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': get_page_obj(request, group.posts.all()),
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    follow = (request.user.is_authenticated
              and not request.user.username == username
              and Follow.objects.filter(author=author,
                                        user=request.user).exists())
    return render(request, 'posts/profile.html', {
        'author': author,
        'page_obj': get_page_obj(request, author.posts.all()),
        'following': follow
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'form': CommentForm(),
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)
    form = PostForm(request.POST or None,
                    instance=post,
                    files=request.FILES or None)
    if not form.is_valid():
        context = {
            'form': form,
            'is_edit': True
        }
        return render(request, 'posts/create_post.html', context)
    form.save()
    return redirect('posts:post_detail', post_id=post.id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def profile_follow(request, username):
    if not (request.user.username == username or Follow.objects.filter(
            author__username=username, user=request.user).exists()):
        Follow.objects.create(
            user=request.user,
            author=get_object_or_404(User, username=username)
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    if (request.user.username != username and Follow.objects.filter(
            author__username=username, user=request.user).exists()):
        get_object_or_404(Follow, author__username=username,
                          user=request.user).delete()
    return redirect('posts:profile', username=username)
