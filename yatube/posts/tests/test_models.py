from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Group, Post, Comment


User = get_user_model() 


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост JOJO JOJO JOJO',
        )
        cls.comment = Comment.objects.create(
            post = cls.post,
            author = cls.user,
            text = 'Test_text' * 10
        )


    def test_models_str_post(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        expected = post.text[:15]
        self.assertEqual(
            expected,
            str(post),
            'С возвратом __str__ в модели Post что-то не так'
        )

    def test_models_str_group(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = PostModelTest.group
        expected = group.title
        self.assertEqual(
            expected,
            str(group),
            'С возвратом __str__ в модели Group что-то не так'
        )

    def test_models_str_comment(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        comment = PostModelTest.comment
        expected = comment.text[:15]
        self.assertEqual(
            expected,
            str(comment),
            'С возвратом __str__ в модели Group что-то не так'
        )

    def test_models_verbose_name_post(self):
        """Проверяем, что у модели Post ожидаемое значение verbose_name.""" 
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value,
                    'В моделе Post verbose_name не соответствует запланированным'
                )

    def test_models_verbose_name_comment(self):
        """Проверяем, что у модели Comment ожидаемое значение verbose_name."""
        comment = PostModelTest.comment
        field_verboses = {
            'post': 'Комментарий',
            'author': 'Автор',
            'text': 'Текст',
            'created': 'Дата публикации'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(fielf=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name,
                    expected_value,
                    'В моделе Comment verbose_name не соответствует запланированным'
                )

    def test_models_help_text_post(self):
        """Проверяем, что у модели Post ожидаемое значение help_text."""
        post = PostModelTest.post
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value,
                    'Поле help_text модели Post не соответствует ожиданиям'
                )

    def test_models_help_text_comment(self):
        """Проверяем, что у модели Comment ожидаемое значение help_text."""
        comment = PostModelTest.comment
        self.assertEqual(
            comment._meta.get_field('text').help_text,
            'Введите текст комментария',
            'Поле help_text модели Comment не соответствует ожиданиям'
        )
