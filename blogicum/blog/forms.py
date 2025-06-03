from django import forms
from .models import Post
from django import forms
from .models import Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "text", "pub_date", "category", "location", "image"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]  # или ваш список полей
