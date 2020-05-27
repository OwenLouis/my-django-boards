# -*- coding:utf-8 -*-
# Create your tests here.
from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User

from ..forms import NewTopicForm
from ..models import Board, Topic, Post
from ..views import new_topic


class NewTopicsTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', desc='Django board.')
        username = 'john'
        password = '123'
        User.objects.create_user(username=username, email='john@doe.com', password=password)
        self.url = reverse('new_topic', kwargs={'pk': 1})
        self.client.login(username=username, password=password)

    def test_new_topic_view_success_status_code(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_new_topic_view_not_found_status_code(self):
        url = reverse('new_topic', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_new_topic_url_resolves_new_topic_view(self):
        view = resolve('/boards/1/new/')
        self.assertEquals(view.func, new_topic)

    def test_new_topics_view_contains_link_back_to_board_topics_view(self):
        # new_topic_url = reverse('new_topic', kwargs={'pk': 1})
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(self.url)
        self.assertContains(response, 'href="{0}"'.format(board_topics_url))

    def test_csrf(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

    def test_new_topic_valid_post_data(self):
        data = {
            'subject': 'Test title',
            'message': 'Test message'
        }
        response = self.client.post(self.url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test_new_topic_invalid_post_data(self):
        response = self.client.post(self.url, {})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_new_topic_invalid_post_data_empty_fields(self):
        data = {
            'subject': '',
            'message': ''
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())


class LoginRequiredNewTopicTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', desc='Django board.')
        self.url = reverse('new_topic', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, f'{login_url}?next={self.url}')
