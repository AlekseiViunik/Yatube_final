import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа раз',
            description='Тестовое описание группы',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            pub_date='Тестовая дата',
            group=cls.group,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        return super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверяем, что форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст1',
            'group': self.group.id,
            'image': uploaded
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст1',
                group=self.group.id,
            ).exists()
        )

    def test_edit_post(self):
        """Проверяем, что форма изменяет запись."""
        posts_count = Post.objects.count()
        form_data_changed = {
            'text': 'Тестовый текст2',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data_changed,
            follow=True,
        )
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        response_post = response.context.get('post')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response_post.group.id, form_data_changed['group'])
        self.assertEqual(response_post.text, form_data_changed['text'])

    def test_labels(self):
        """Проверяем лейблы."""
        labels_expected = {
            'text': 'Пост',
            'group': 'группа:',
        }
        for value, expected in labels_expected.items():
            with self.subTest(value=value):
                show_label = PostFormsTest.form.fields[value].label
                self.assertEquals(show_label, expected)

    def test_help_text(self):
        """Проверяем хелп_текст."""
        help_texts_expected = {
            'text': 'Тут пишите буквы',
            'group': 'Выберите из доступных:',
        }
        for value, expected in help_texts_expected.items():
            with self.subTest(value=value):
                show_help_text = PostFormsTest.form.fields[value].help_text
                self.assertEquals(show_help_text, expected)
