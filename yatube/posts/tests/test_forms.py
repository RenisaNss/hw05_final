from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Post, Group, Comment
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile


User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username = 'Test_name'
        )
        cls.group = Group.objects.create(
            title = 'Test_title_group',
            slug = 'test_slug_group'
        )
        cls.post = Post.objects.create(
            text = 'Test_text',
            author = cls.user,
            group = cls.group
        )
        cls.comment = Comment.objects.create(
            post = cls.post,
            author = cls.user,
            text = 'Test_comment'
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = PostCreateFormTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    
    def test_create_post(self):
        """Проверка создания новой записи в модели Post"""
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
            'text': 'Test_text',
            'group': PostCreateFormTests.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.post.author}
        ))
        
        self.assertEqual(
            Post.objects.count(),
            posts_count+1
        )
        self.assertTrue(
            Post.objects.filter(
                text='Test_text',
                author=self.user,
                group = PostCreateFormTests.group,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        """Проверка изменения поста"""
        form_data = {
            'text': 'chanje_text',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostCreateFormTests.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail',
                kwargs={'post_id': PostCreateFormTests.post.id}
            )
        )
        self.assertTrue(
            Post.objects.filter(
                text='chanje_text'
            ).exists()
        )

    def test_add_comment(self):
        """Проверка добавления комментария"""
        comment_count = Comment.objects.count()
        form_data = {
            'post': PostCreateFormTests.post.id,
            'author': PostCreateFormTests.user.id,
            'text': 'Test_comment_2',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment',
            kwargs={'post_id': PostCreateFormTests.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostCreateFormTests.post.id})
            )
        self.assertEqual(Comment.objects.count(), comment_count+1)
        self.assertTrue(
            Comment.objects.filter(
                post = PostCreateFormTests.post.id,
                author = PostCreateFormTests.user.id,
                text = 'Test_comment_2',
            ).exists()
        )
