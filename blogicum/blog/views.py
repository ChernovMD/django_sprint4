from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import (
    DetailView,
    UpdateView,
    CreateView,
    DeleteView,
)

from core.utils import post_all_query, post_published_query, get_post_data
from core.mixins import CommentMixinView
from .models import Post, User, Category, Comment
from .forms import UserEditForm, PostEditForm, CommentEditForm
from django.utils import timezone


from django.views import View
from django.shortcuts import render
from core.utils import get_page


class MainPostListView(View):
    """Главная страница со списком постов с ручной пагинацией."""

    template_name = "blog/index.html"
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        queryset = post_published_query()
        page_obj = get_page(request, queryset, self.paginate_by)
        return render(request, self.template_name, {"page_obj": page_obj})


class CategoryPostListView(View):
    template_name = "blog/category.html"
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        queryset = post_published_query().filter(category=category)
        page_obj = get_page(request, queryset, self.paginate_by)
        extra_categories = Category.objects.filter(
            slug__in=["news", "science", "travel"], is_published=True
        )
        return render(
            request,
            self.template_name,
            {
                "page_obj": page_obj,
                "category": category,
                "extra_categories": extra_categories,
            },
        )


class UserPostsListView(View):
    template_name = "blog/profile.html"
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        author = get_object_or_404(User, username=self.kwargs["username"])
        if author == request.user:
            queryset = post_all_query().filter(author=author)
        else:
            queryset = post_published_query().filter(author=author)
        page_obj = get_page(request, queryset, self.paginate_by)
        return render(
            request, self.template_name,
            {"page_obj": page_obj, "profile": author}
        )


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"
    post_data = None
    pk_url_kwarg = "post_id"

    def get_queryset(self):
        self.post_data = get_object_or_404(Post, pk=self.kwargs["post_id"])
        if self.post_data.author == self.request.user:
            return post_all_query().filter(pk=self.kwargs["post_id"])
        return post_published_query().filter(pk=self.kwargs["post_id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.check_post_data():
            context["flag"] = True
            context["form"] = CommentEditForm()
        context["comments"] =\
            self.object.comments.all().select_related("author")
        return context

    def check_post_data(self):
        """Вернуть результат проверки поста."""
        return all(
            (
                self.post_data.is_published,
                self.post_data.pub_date <= now(),
                self.post_data.category.is_published,
            )
        )


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление профиля пользователя.

    Атрибуты:
        - model: Класс модели, используемой для получения данных.
        - form_class: Класс формы, используемый для обновления профиля
        пользователя.
        - template_name: Имя шаблона, используемого для отображения страницы.

    Методы:
        - get_object(queryset=None): Возвращает объект пользователя для
        обновления.
        - get_success_url(): Возвращает URL-адрес для перенаправления после
        успешного обновления профиля.
    """

    model = User
    form_class = UserEditForm
    template_name = "blog/user.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        username = self.request.user
        return reverse("blog:profile", kwargs={"username": username})


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста.

    Атрибуты:
        - model: Класс модели, используемой для создания поста.
        - form_class: Класс формы, используемый для создания поста.
        - template_name: Имя шаблона, используемого для отображения страницы.

    Методы:
        - form_valid(form): Проверяет, является ли форма допустимой,
        и устанавливает автора поста.
        - get_success_url(): Возвращает URL-адрес для перенаправления после
        успешного создания поста.
    """

    model = Post
    form_class = PostEditForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.pub_date = timezone.now()
        form.instance.is_published = True
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user
        return reverse("blog:profile", kwargs={"username": username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование поста.

    Атрибуты:
        - model: Класс модели, используемой для редактирования поста.
        - form_class: Класс формы, используемый для редактирования поста.
        - template_name: Имя шаблона, используемого для отображения страницы.

    Методы:
        - dispatch(request, *args, **kwargs): Проверяет, является ли
        пользователь автором поста.
        - get_success_url(): Возвращает URL-адрес перенаправления после
        успешного редактирования поста.
    """

    model = Post
    form_class = PostEditForm
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", post_id=self.kwargs["post_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        post_id = self.kwargs["post_id"]
        return reverse("blog:post_detail", kwargs={"post_id": post_id})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление поста.

    Атрибуты:
        - model: Класс модели, используемой для удаления поста.
        - template_name: Имя шаблона, используемого для отображения страницы.

    Методы:
        - dispatch(request, *args, **kwargs): Проверяет, является ли
        пользователь автором поста.
        - get_context_data(**kwargs): Возвращает контекстные данные для
        шаблона.
        - get_success_url(): Возвращает URL-адрес перенаправления после
        успешного удаления поста.
    """

    model = Post
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", post_id=self.kwargs["post_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostEditForm(instance=self.object)
        return context

    def get_success_url(self):
        username = self.request.user
        return reverse_lazy("blog:profile", kwargs={"username": username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария.

    Атрибуты:
        - model: Класс модели, используемой для создания комментария.
        - form_class: Класс формы, используемый для создания комментария.
        - template_name: Имя шаблона, используемого для отображения страницы.
        - post_data: Объект поста, к которому создается комментарий.

    Методы:
        - dispatch(request, *args, **kwargs): Получает объект поста.
        - form_valid(form): Проверяет, является ли форма допустимой,
        и устанавливает автора комментария.
        - get_success_url(): Возвращает URL-адрес перенаправления после
        успешного создания комментария.
        - send_author_email(): Отправляет email автору поста, при добавлении
        комментария.
    """

    model = Comment
    form_class = CommentEditForm
    template_name = "blog/comment.html"
    post_data = None

    def dispatch(self, request, *args, **kwargs):
        self.post_data = get_post_data(self.kwargs)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_data
        if self.post_data.author != self.request.user:
            self.send_author_email()
        return super().form_valid(form)

    def get_success_url(self):
        post_id = self.kwargs["post_id"]
        return reverse("blog:post_detail", kwargs={"post_id": post_id})

    def send_author_email(self):
        post_url = self.request.build_absolute_uri(self.get_success_url())
        recipient_email = self.post_data.author.email
        subject = "New comment"
        message = (
            f"Пользователь {self.request.user} добавил "
            f"комментарий к посту {self.post_data.title}.\n"
            f"Читать комментарий {post_url}"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email="from@example.com",
            recipient_list=[recipient_email],
            fail_silently=True,
        )


class CommentUpdateView(CommentMixinView, UpdateView):
    """Редактирование комментария.

    CommentMixinView: Базовый класс, предоставляющий функциональность.

    Атрибуты:
        - form_class: Класс формы, используемый для редактирования
        комментария.
    """

    form_class = CommentEditForm


class CommentDeleteView(CommentMixinView, DeleteView):
    """Удаление комментария."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.pop("form", None)  # 💥 удаляем форму
        return context
