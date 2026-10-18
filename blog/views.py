import uuid
from pathlib import Path

from PIL import Image
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from .forms import AboutMeForm, BlogPostForm, CommentForm, RegisterForm
from .models import AboutMe, BlogPost, Comment

User = get_user_model()


def blog_home(request):
    authors = User.objects.filter(blog_posts__isnull=False).distinct().order_by('username')
    queryset = BlogPost.objects.select_related('author').annotate(comment_count=Count('comments'))
    query = request.GET.get('q', '').strip()
    tag = request.GET.get('tag', '').strip()
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    if tag:
        queryset = queryset.filter(tags__icontains=tag)
    paginator = Paginator(queryset, 10)
    page = request.GET.get('page', 1)
    latest_posts = paginator.get_page(page)
    return render(request, 'blog/blog_home.html', {
        'authors': authors,
        'latest_posts': latest_posts,
        'query': query,
        'tag': tag,
    })


def author_detail(request, username):
    author = get_object_or_404(User, username=username)
    queryset = author.blog_posts.select_related('author').annotate(comment_count=Count('comments'))
    paginator = Paginator(queryset, 10)
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)
    return render(request, 'blog/author_detail.html', {
        'author': author,
        'posts': posts,
    })


def post_detail(request, username, pk):
    post = get_object_or_404(BlogPost, pk=pk, author__username=username)
    comments = post.comments.filter(parent__isnull=True).select_related('author').prefetch_related(
        Prefetch('replies', queryset=Comment.objects.select_related('author').order_by('created_at'))
    )
    form = CommentForm()
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })


@require_POST
def comment_create(request, username, pk):
    post = get_object_or_404(BlogPost, pk=pk, author__username=username)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        parent_pk = request.POST.get('parent')
        if parent_pk:
            parent = get_object_or_404(Comment, pk=parent_pk, post=post)
            comment.parent = parent
        if request.user.is_authenticated:
            comment.author = request.user
        comment.save()
        messages.success(request, _('评论已发表'))
    else:
        messages.error(request, _('评论提交失败，请检查验证码'))
    return redirect(post.get_absolute_url())


@login_required
@require_POST
def comment_delete(request, username, pk, comment_pk):
    post = get_object_or_404(BlogPost, pk=pk, author__username=username)
    comment = get_object_or_404(Comment, pk=comment_pk, post=post)
    if request.user == post.author or request.user == comment.author:
        comment.delete()
        messages.success(request, _('评论已删除'))
    else:
        messages.error(request, _('你没有权限删除这条评论'))
    return redirect(post.get_absolute_url())


@login_required
def post_create(request):
    form = BlogPostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, _('博客已发布'))
        return redirect(post.get_absolute_url())
    return render(request, 'blog/post_form.html', {
        'form': form,
        'title': _('写博客'),
    })


@login_required
def post_edit(request, username, pk):
    post = get_object_or_404(BlogPost, pk=pk, author__username=username)
    if request.user != post.author and not request.user.is_superuser:
        messages.error(request, _('你没有权限编辑这篇博客'))
        return redirect(post.get_absolute_url())
    form = BlogPostForm(request.POST or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('博客已更新'))
        return redirect(post.get_absolute_url())
    return render(request, 'blog/post_form.html', {
        'form': form,
        'title': _('编辑博客'),
        'post': post,
    })


@login_required
def post_delete(request, username, pk):
    post = get_object_or_404(BlogPost, pk=pk, author__username=username)
    if request.user != post.author and not request.user.is_superuser:
        messages.error(request, _('你没有权限删除这篇博客'))
        return redirect(post.get_absolute_url())
    if request.method == 'POST':
        post.delete()
        messages.success(request, _('博客已删除'))
        return redirect('blog:author_detail', username=username)
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


def about_me(request):
    about = AboutMe.get_instance()
    return render(request, 'blog/about_me.html', {'about': about})


@login_required
def about_me_edit(request):
    if not request.user.is_superuser:
        messages.error(request, _('只有超级用户可以编辑关于我'))
        return redirect('blog:about_me')
    about = AboutMe.get_instance()
    form = AboutMeForm(request.POST or None, instance=about)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('关于我已更新'))
        return redirect('blog:about_me')
    return render(request, 'blog/about_me_edit.html', {'form': form})


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('注册成功，请登录'))
        return redirect('blog:login')
    return render(request, 'blog/register.html', {'form': form})


def _is_image(file):
    if file.content_type and file.content_type.startswith('image/'):
        return True
    ext = Path(file.name).suffix.lower()
    return ext in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}


@login_required
@require_POST
def upload_media(request):
    files = request.FILES.getlist('files')
    paths = request.POST.getlist('paths')
    if len(paths) != len(files):
        paths = [''] * len(files)

    upload_dir = Path(settings.MEDIA_ROOT) / 'uploads' / request.user.username / uuid.uuid4().hex
    results = []
    for file, rel_path in zip(files, paths):
        rel = (rel_path or file.name).lstrip('/')
        if '..' in rel or rel.startswith('.') and '/' in rel:
            continue

        if _is_image(file):
            rel = str(Path(rel).with_suffix('.webp'))
            target = upload_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                image = Image.open(file)
                if image.mode not in ('RGB', 'RGBA'):
                    image = image.convert('RGB')
                image.save(target, 'WEBP', quality=85)
            except Exception:
                # fallback to original if conversion fails
                file.seek(0)
                with open(target, 'wb') as dest:
                    for chunk in file.chunks():
                        dest.write(chunk)
        else:
            target = upload_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, 'wb') as dest:
                for chunk in file.chunks():
                    dest.write(chunk)

        relative_url = (Path(settings.MEDIA_URL) / 'uploads' / request.user.username / upload_dir.name / rel).as_posix()
        results.append({'url': relative_url, 'name': Path(rel).name, 'path': rel})
    return JsonResponse({'files': results})
