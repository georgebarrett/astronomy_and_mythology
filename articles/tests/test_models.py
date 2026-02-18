from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from articles.models import Article


def test_image_file(filename='test.jpg'):
    return SimpleUploadedFile(
        name=filename,
        content=(
            b'GIF87a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,'
            b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02D\x01\x00;'
        ),
        content_type='image/gif',
    )

class ArticleModelTest(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='autechre',
            password='password'
        )

        self.article = Article.objects.create(
            title = 'Pluto and Hades',
            slug = 'pluto-and-hades',
            body = 'Hades and Pluto are connected',
            author = self.user,
            image = test_image_file(),
            publish = timezone.now()
        )

        self.previous_article = Article.objects.create(
            title = 'previous article',
            slug = 'previous-article',
            body = 'test body',
            author = self.user,
            image = test_image_file(),
            publish = timezone.now() - timezone.timedelta(days=1)
        )

    def test_article_is_created(self):
        self.assertEqual(Article.objects.count(), 2)

    def test_article_fields_are_saved(self):
        self.assertEqual(self.article.title, 'Pluto and Hades')
        self.assertEqual(self.article.slug, 'pluto-and-hades')
        self.assertEqual(self.article.body, 'Hades and Pluto are connected')
        self.assertEqual(self.article.author, self.user)

    def test_ordering_is_descending(self):
        articles = Article.objects.all()
        self.assertEqual(articles[0], self.article)
        self.assertEqual(articles[1], self.previous_article)

    def test_slug_must_be_unique(self):
        with self.assertRaises(IntegrityError):
            Article.objects.create(
                title = 'duplicate slug',
                slug = 'pluto-and-hades',
                author = self.user,
                body = 'test body',
                image = test_image_file('ozzy.jpg'),
                publish = timezone.now()
            )

    def test_image_is_required(self):
        article = Article(
            title = 'image please',
            slug = 'image-please',
            author = self.user,
            body = 'no image',
            publish = timezone.now()
        )

        with self.assertRaises(ValidationError):
            article.full_clean()

    def test_str_returns_title(self):
        self.assertEqual(str(self.article), 'Pluto and Hades')

    def test_default_status_is_draft(self):
        self.assertEqual(self.article.status, Article.Status.DRAFT)

    def test_created_and_updated_fields_are_set(self):
        self.assertIsNotNone(self.article.created)
        self.assertIsNotNone(self.article.updated)
