from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': ('Пост'),
            'group': ('группа:'),
        }
        help_texts = {
            'text': ('Тут пишите буквы'),
            'group': ('Выберите из доступных:'),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': ('Комментарий'),
        }
        help_texts = {
            'text': ('Тут пишите вашу предъяву'),
        }
