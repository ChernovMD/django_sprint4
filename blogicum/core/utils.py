from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone

from blog.models import Post
from django.core.paginator import Paginator


def annotate_comment_count(queryset):
    """Добавить аннотацию количества комментариев и применить сортировку."""
    return queryset.annotate(
        comment_count=Count("comments")).order_by("-pub_date")


def post_all_query():
    """Вернуть все посты с аннотацией количества комментариев."""
    query_set = Post.objects.select_related(
        "category",
        "location",
        "author",
    )
    return annotate_comment_count(query_set)


def post_published_query():
    """Вернуть опубликованные посты с аннотацией количества комментариев."""
    query_set = post_all_query().filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__isnull=False,
        category__is_published=True,
    )
    return query_set


def get_post_data(post_data):
    """Вернуть объект поста по id и проверке публикации."""
    return get_object_or_404(
        Post,
        pk=post_data["post_id"],
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )


def get_page(request, queryset, per_page=10):
    """Вернуть одну страницу из пагинатора."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
