import shutil
import tempfile
from django.conf import settings
from django.urls import reverse
from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from posts.models import Post, Group, Follow
from django.core.files.uploadedfile import SimpleUploadedFile

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='Test_name'
        )
        cls.group = Group.objects.create(
            title='Test_title',
            slug='test_slug'
        )
        cls.group_without_posts = Group.objects.create(
            title='Test_title_without_posts',
            slug='test_title_without_posts'
        )
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
        cls.post = Post.objects.create(
            text='Test_text_0',
            group=cls.group,
            author=cls.user,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

        self.user = PostViews.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_name_space(self):
        """Проверка вызываемых шаблонов по namespace."""
        dct = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{PostViews.group.slug}'}):
                'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}):
                'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{PostViews.post.id}'}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{PostViews.post.id}'}):
                'posts/create_post.html',
        }

        for reverse_name, template in dct.items():
            with self.subTest(reverse_name = reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_page_obj_in_index_group_profile(self):
        """Проверка правильного списка записей переданного в контекст."""
        lst_reverse_name = [
            self.authorized_client.get(reverse('posts:index')),
            self.authorized_client.get(
                reverse(
                    'posts:group_list',
                    kwargs={'slug': f'{PostViews.group.slug}'}
                )),
            self.authorized_client.get(
                reverse(
                    'posts:profile',
                    kwargs={'username': f'{self.user}'}
                ))
        ]
        for response in lst_reverse_name:
            with self.subTest(response=response):
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.text, PostViews.post.text)
                self.assertEqual(
                    first_object.group.title,
                    PostViews.group.title
                )
                self.assertEqual(first_object.author, PostViews.user)
                self.assertEqual(first_object.image, PostViews.post.image)

    def test_context_post_detail(self):
        """Страница одного поста "post_detail"
        возвращает правильный контекст.
        """
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': f'{PostViews.post.id}'}
        ))
        object = response.context.get('post')
        self.assertEqual(object.text, PostViews.post.text)
        self.assertEqual(object.author, self.user)
        self.assertEqual(object.group, PostViews.group)
        self.assertEqual(object.image, PostViews.post.image)
        self.assertEqual(
            object.author.posts.count(), PostViews.post.author.posts.count()
        )
        form_field = response.context.get('form').fields.get('text')
        self.assertIsInstance(form_field, forms.fields.CharField)

    def test_form_create_and_edit_post(self):
        """Проверка ожидаемых виджетов полей формы."""
        lst = [
            self.authorized_client.get(reverse('posts:post_create')),
            self.authorized_client.get(
                reverse(
                    'posts:post_edit',
                    kwargs={'post_id': f'{PostViews.post.id}'})
            )
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for response in lst:
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_create_post_home_group_list_profile_pages(self):
        """Созданный пост с группой отобразился на главной,
        на странице группы и в профиле пользователя.
        """
        list_urls = (
            reverse('posts:index'),
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PostViews.post.author.username}
            ),
        )
        for tested_url in list_urls:
            response = self.authorized_client.get(tested_url)
            self.assertEqual(len(response.context['page_obj']), 1)

    def test_group_without_posts(self):
        """Пост не попал в группу, для которой не был предназначен."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': f'{PostViews.group_without_posts.slug}'}
        ))
        self.assertEqual(len(response.context['page_obj']), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='Test_name'
        )
        cls.group = Group.objects.create(
            title='Test_title',
            slug='test_slug'
        )
        cls.posts = []

        for i in range(13):
            cls.posts.append(Post(
                text=f'Test_text_{i + 1}',
                group=cls.group,
                author=cls.user,)
            )
            cls.posts[i].save()

    def setUp(self):
        self.user = PaginatorViewsTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator_second_page(self):
        """Пагинатор возвращает на 1стр.
        10 постов, на 2стр. 3 поста.
        """
        lst_numb_page_paginator = ['1_page', '2_page']
        lst_revese_name = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug}),
            reverse(
                'posts:profile', kwargs={'username': self.user})
        ]

        for num_page in lst_numb_page_paginator:
            for reverse_name in lst_revese_name:
                with self.subTest(reverse_name=reverse_name):
                    if num_page == 'page_2':
                        response = self.authorized_client.get(
                            reverse_name, {'page': 2}
                        )
                        # Либо так:(reverse_name + '?page=2')
                        self.assertEqual(
                            len(response.context['page_obj']), 3
                        )
                    else:
                        response = self.authorized_client.get(
                            reverse_name
                        )
                        self.assertEqual(
                            len(response.context['page_obj']), 10
                        )


class PostViewsFollow(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='Test_name'
        )
        cls.author = User.objects.create(
            username='Test_author'
        )
        cls.post = Post.objects.create(
            text='Test_text_0',
            author=cls.user,
        )
        cls.post_of_author = Post.objects.create(
            text='Test_text_of_author',
            author=cls.author,
        )

    def setUp(self):
        self.user = PostViewsFollow.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_follow(self):
        """Авторизованный пользователь может подписываться
        на других пользователей и удалять их из подписок.
        """
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostViewsFollow.author.username}
            )
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=PostViewsFollow.author
            ).exists()
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostViewsFollow.author.username}
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=PostViewsFollow.author
            )
        )

    def test_follow_not_himself(self):
        """Автор не может подписаться сам на себя"""
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user.username}
            )
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(
            len(response.context['page_obj']), 0
        )

    def test_follow_posts_not_exists(self):
        """Новая запись пользователя не появляется в ленте тех,
        кто на него не подписан.
        """
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(
            len(response.context['page_obj']), 0
        )

    def test_follow_posts_exists(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан.
        """
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostViewsFollow.author.username}
            )
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(
            len(response.context['page_obj']), 1
        )
