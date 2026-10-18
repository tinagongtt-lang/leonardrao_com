from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import BlogPostForm, sanitize_html
from .models import BlogPost, Comment

User = get_user_model()


class SanitizeHtmlTests(TestCase):
    def test_removes_script(self):
        raw = '<p>ok</p><script>alert(1)</script>'
        self.assertNotIn('<script', sanitize_html(raw))
        self.assertIn('<p>ok</p>', sanitize_html(raw))

    def test_removes_onload(self):
        raw = '<img src="x" onload="alert(1)">'
        result = sanitize_html(raw)
        self.assertNotIn('onload', result)

    def test_removes_javascript_href(self):
        raw = '<a href="javascript:alert(1)">link</a>'
        result = sanitize_html(raw)
        self.assertNotIn('href', result)


class BlogPostTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='testpass123')

    def test_create_post(self):
        post = BlogPost.objects.create(author=self.user, title='Hello', content='<p>World</p>')
        self.assertEqual(str(post), 'Hello')
        self.assertTrue(post.get_absolute_url().endswith(f'/blog/tester/{post.pk}/'))

    def test_form_sanitizes_content(self):
        form = BlogPostForm(data={
            'title': 'XSS',
            'tags': 'a,b',
            'content': '<p>safe</p><script>alert(1)</script>',
        })
        self.assertTrue(form.is_valid())
        post = form.save(commit=False)
        post.author = self.user
        post.save()
        self.assertNotIn('<script', post.content)


class CommentTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='author', password='pass1234')
        self.commenter = User.objects.create_user(username='commenter', password='pass1234')
        self.post = BlogPost.objects.create(author=self.author, title='Post', content='<p>Body</p>')

    def test_top_level_comment(self):
        comment = Comment.objects.create(post=self.post, content='Nice', author=self.commenter)
        self.assertEqual(self.post.comments.first(), comment)

    def test_reply(self):
        parent = Comment.objects.create(post=self.post, content='Parent')
        reply = Comment.objects.create(post=self.post, content='Reply', parent=parent)
        self.assertIn(reply, parent.replies.all())

    def test_comment_create_view(self):
        self.client.force_login(self.commenter)
        url = reverse('blog:comment_create', kwargs={'username': 'author', 'pk': self.post.pk})
        response = self.client.post(url, {'content': 'Great post', 'captcha_0': 'dummy', 'captcha_1': 'dummy'})
        self.assertEqual(response.status_code, 302)
