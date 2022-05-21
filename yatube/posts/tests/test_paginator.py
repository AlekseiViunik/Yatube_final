from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from yatube.settings import NUMBER_OF_POSTS

User = get_user_model()

POSTS_AMOUNT = NUMBER_OF_POSTS + 3


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Текстовая группа',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.posts = (
            Post(
                author=cls.user,
                text=f'Текст поста {i}',
                pub_date='Тестовая дата',
                group=cls.group,
            ) for i in range(POSTS_AMOUNT)
        )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_contain_right_amount_of_records(self):
        amount_for_reverse = {
            reverse('posts:index'): NUMBER_OF_POSTS,
            reverse('posts:index') + '?page=2': POSTS_AMOUNT - NUMBER_OF_POSTS
        }
        for reverse_name, amount in amount_for_reverse.items():
            response = self.authorized_client.get(reverse_name)
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(len(response.context['page_obj']), amount)
