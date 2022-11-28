from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Post, Group
from http import HTTPStatus


User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name_test')
        cls.user2 = User.objects.create_user(username='Name_test_2')
        cls.group = Group.objects.create(
            title='Test_title',
            slug='Test_slug',
            description='Test_description'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test_text',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = StaticURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.user2 = StaticURLTests.user2
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user2)

    def test_urls_users_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{StaticURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{StaticURLTests.post.pk}/': 'posts/post_detail.html',
            f'/posts/{StaticURLTests.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
            '/unexisting_page/': 'core/404.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_loop_anonim(self):
        """Проверяет доступны ли общедоступные
        страницы по ожидаемому адресу.
        """
        lst_clients = [
            self.guest_client,
            self.authorized_client
        ]
        lst_address = [
            '/',
            f'/group/{StaticURLTests.group.slug}/',
            f'/profile/{self.user}/',
            f'/posts/{StaticURLTests.post.pk}/'
        ]
        for client in lst_clients:
            for adress in lst_address:
                with self.subTest(adress=adress):
                    response = client.get(adress)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_edit(self):
        """Страница /posts/1/edit/ доступна
        только авторизованному пользователю.
        """
        response = self.authorized_client.get(
            f'/posts/{StaticURLTests.post.pk}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_not_posts_edit(self):
        """Страница по адресу /posts/1/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(
            f'/posts/{StaticURLTests.post.pk}/edit/',
            follow=True
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{StaticURLTests.post.pk}/edit/'
        )

    def test_not_posts_edit_authoriz(self):
        """Страница по адресу /posts/1/edit/ перенаправит авторизованного
        пользователя на страницу поста, если это не его пост.
        """
        response = self.authorized_client_2.get(
            f'/posts/{self.post.pk}/edit/',
            follow=True
        )
        self.assertRedirects(response, f'/posts/{StaticURLTests.post.pk}/')

    def test_create(self):
        """Страница /create/ доступна только авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_not_comment(self):
        """Страница по адресу /posts/id_post/comment/ перенаправит
        анонимного пользователя на страницу логина.
        """
        response = self.guest_client.get(
            f'/posts/{StaticURLTests.post.pk}/comment/'
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{StaticURLTests.post.pk}/comment/'
        )

    def test_comment(self):
        """Страница по адресу /posts/id_post/comment/ перенаправит
        зарегистрированного пользователя на страницу /posts/id_post/.
        """
        response = self.authorized_client.get(
            f'/posts/{StaticURLTests.post.pk}/comment/'
        )
        self.assertRedirects(response, f'/posts/{StaticURLTests.post.pk}/')

    def test_follow_page(self):
        """Страница постов авторов по подписке
        доступны только авторизованному пользователю
        """
        response = self.guest_client.get('/follow/', follow=True)
        self.assertRedirects(
            response,
            '/auth/login/?next=/follow/'
        )
        response = self.authorized_client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_follow(self):
        """Страница подписки доступна только авторизованному пользователю"""
        response = self.guest_client.get(
            f'/profile/{self.user}/follow/',
            follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/profile/{self.user}/follow/'
        )
        response = self.authorized_client.get(
            f'/profile/{self.user2}/follow/'
        )
        self.assertRedirects(
            response, f'/profile/{self.user2}/'
        )

    def test_unfollow(self):
        """Страница отписки доступна только авторизованному пользователю"""
        response = self.guest_client.get(
            f'/profile/{self.user}/unfollow/',
            follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/profile/{self.user}/unfollow/'
        )
        response = self.authorized_client.get(
            f'/profile/{self.user2}/unfollow/'
        )
        self.assertRedirects(
            response, f'/profile/{self.user2}/'
        )

    def test_404_error(self):
        """Несуществующая страница /unexisting_page/ возвращает 404"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
