from django import forms

from .models import User, Post, Comment


class UserEditForm(forms.ModelForm):
    """Форма редактирования информации о пользователе."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")


class PostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "title",
            "text",
            "image",
            "category",
            "location",
            "is_published",  # ✅ добавлено
            "pub_date",       # ✅ добавлено
        )
        widgets = {
            "text": forms.Textarea({"rows": "5"}),
            "pub_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class CommentEditForm(forms.ModelForm):
    """Форма редактирования комментария."""

    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {
            "text": forms.Textarea({"rows": "3"})
        }
