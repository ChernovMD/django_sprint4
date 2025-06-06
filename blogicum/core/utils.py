from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone

from blog.models import Post


def post_all_query():
    """Вернуть все посты с аннотацией количества комментариев."""
    query_set = Post.objects.select_related(
        "category",
        "location",
        "author",
    ).order_by("-pub_date")

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
    """Вернуть данные поста.

    Ограничивает возможность авторов писать и редактировать комментарии
    к постам снятым с публикации, постам в категориях снятых с публикации,
    постам дата публикации которых больше текущей даты.
    Проверяет:
        - Пост опубликован.
        - Категория в которой находится пост опубликована.
        - Дата поста не больше текущей даты.

    Возвращает: Объект или 404
    """
    post = get_object_or_404(
        Post,
        pk=post_data["post_id"],
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )
    return post


from django.db.models import Count

def annotate_comment_count(queryset):
    """Добавить аннотацию количества комментариев к постам."""
    return queryset.annotate(comment_count=Count("comments"))
