from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Post, Category
from .forms import PostForm, CommentForm


def index(request):
    posts = (
        Post.objects.select_related("category")
        .filter(
            is_published=True, pub_date__lte=timezone.now(),
            category__is_published=True
        )
        .order_by("-pub_date")
    )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "blog/index.html", {"page_obj": page_obj})


def post_detail(request, pk):
    post = get_object_or_404(
        Post.objects.select_related("author", "location", "category"),
        pk=pk,
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    )
    return render(request, "blog/detail.html", {"post": post})


def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug,
                                 is_published=True)
    posts = category.post_set.filter(
        is_published=True, pub_date__lte=timezone.now()
    ).order_by("-pub_date")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request, "blog/category.html",
        {"category": category, "page_obj": page_obj}
    )


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("blog:profile", username=request.user.username)
    else:
        form = PostForm()
    return render(request, "blog/create.html", {"form": form})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, "blog/edit_post.html", {"form": form, "post": post})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user == post.author or request.user.is_staff:
        post.delete()
        return redirect("blog:index")
    return redirect("blog:post_detail", pk=pk)


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect("blog:post_detail", pk=post.pk)
    else:
        form = CommentForm()
    return render(request, "blog/add_comment.html",
                  {"form": form, "post": post})
