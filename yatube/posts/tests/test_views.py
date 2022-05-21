from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post
from posts.forms import CommentForm, PostForm

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.another_user = User.objects.create_user(username='Another_User')
        cls.follower_user = User.objects.create_user(username='Follower_User')
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
        cls.group2 = Group.objects.create(
            title='Тестовая группа два',
            description='Тестовое описание группы',
            slug='test-slug2'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.another_user,
            text='Тестовый комментарий',
            created='Тестовая дата',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_follower = Client()
        self.authorized_follower.force_login(self.follower_user)
        self.authorized_another = Client()
        self.authorized_another.force_login(self.another_user)
        cache.clear()

    def test_usage_cache_works(self):
        """Проверяем, что кеш главной страницы работает"""
        post = Post.objects.create(
            text='Тестовый пост для кеша',
            author=PostPagesTests.user,
        )
        response = self.authorized_client.get(reverse('posts:index'))
        count_before_delete = len(response.context.get('page_obj'))
        post.delete()
        count_after_delete = len(response.context.get('page_obj'))
        self.assertEqual(count_before_delete, count_after_delete)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        count_cache_clear = len(response.context.get('page_obj'))
        self.assertEqual(count_cache_clear, count_before_delete - 1)

    def test_pages_uses_correct_template(self):
        """Проверяем, что URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:follow_index'): 'posts/follow.html',
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.post.author.username},
            ): 'posts/profile.html',
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.post.author.username},
            ): 'posts/profile.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(
                    reverse_name, follow=True
                )
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Проверяем, что шаблон главной страницы сформирован с правильным
        контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.context.get('page_obj')[0], self.post)
        self.assertEqual(response.context.get('title'), 'Последние записи')
        self.assertTrue(response.context.get('index'))

    def test_group_list_page_show_correct_context(self):
        """Проверяем, что шаблон страницы записей группы сформирован с
        правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': self.post.group.slug})
        )
        self.assertEqual(response.context.get('page_obj')[0], self.post)
        self.assertEqual(response.context.get('title'), 'Записи сообщества')
        self.assertEqual(response.context.get('group'), self.post.group)

    def test_profile_page_show_correct_context(self):
        """Проверяем, что шаблон страницы записей автора сформирован с
        правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            ),
        )
        self.assertEqual(response.context.get('page_obj')[0], self.post)
        self.assertEqual(response.context.get('title'), 'Профайл пользователя')
        self.assertEqual(response.context.get('author'), self.post.author)
        self.assertEqual(
            response.context.get('post_counter'),
            Post.objects.filter(author=self.post.author).count()
        )
        self.assertFalse(response.context.get('following'))

    def test_page_detail_show_correct_context(self):
        """Проверяем, что шаблон page_detail сформирован с правильным
        конекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id},
            )
        )
        self.assertEqual(response.context.get('post'), self.post)
        self.assertEqual(
            response.context.get('post_counter'),
            Post.objects.filter(author=self.post.author).count()
        )
        self.assertIsInstance(response.context.get('form'), CommentForm)
        self.assertIn(self.comment, response.context.get('comments'))

    def test_post_create_page_show_correct_context(self):
        """Проверяем, что шаблон create сформирован с правильным
        контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertFalse(response.context.get('is_edit'))

    def test_post_edit_page_show_correct_context(self):
        """Проверяем, что шаблон edit сформирован с правильным
        контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertEqual(response.context.get('post'), self.post)
        self.assertTrue(response.context.get('is_edit'))

    def test_post_exists_in_index_group_profile(self):
        """Проверяем, что созданный пост появился на главной странице,
        странице группы и на странице постов автора."""
        reverses_filters_dict = {
            reverse('posts:index'): Post.objects.all(),
            reverse('posts:group', kwargs={'slug': self.post.group.slug}):
                Post.objects.filter(group=self.post.group),
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            ): Post.objects.filter(author=self.post.author),
        }
        for reverse_name, filters in reverses_filters_dict.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertTrue(filters.exists())

    def test_post_does_not_exist_in_another_group(self):
        """Проверяем, что созданный пост не появился в другой группе."""
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': self.group2.slug})
        )
        self.assertNotIn(self.post, response.context.get('page_obj'))

    def test_comment_exists(self):
        """Проверяем, что комментарий существует."""
        self.assertIs(self.post, self.comment.post)

    def test_followers_views_work(self):
        """Проверяем, что новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан"""
        Follow.objects.create(user=self.follower_user, author=self.user)
        response = self.authorized_follower.get(reverse('posts:follow_index'))
        self.assertEqual(response.context.get('post'), self.post)
        response = self.authorized_another.get(reverse('posts:follow_index'))
        self.assertNotEqual(response.context.get('post'), self.post)
