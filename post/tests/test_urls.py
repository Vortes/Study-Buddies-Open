from django.test import TestCase
from django.urls import reverse, resolve
from django.utils import timezone
from django.contrib.auth.models import User
from post.views import home_view, post_view, create_view, detail_view
from post.models import Post, Tag, Category


class TestUrls(TestCase):

    # def setUp(self):
    #     self.user = User.objects.create_user(username='testuser', password='12345')
    #     self.category = Category("Maths & Sciences")
    #     self.tag = Tag("Algebra", self.category)
    #     self.post = Post("Test", "Content", timezone.now, author=self.user, subject=self.tag, num_participants=1, max_buddies=5 )
        
    def test_home_url_is_resolved(self):
        url = reverse("post-info")
        self.assertEquals(resolve(url).func, home_view)
    
    def test_post_url_is_resolved(self):
        url = reverse("post-home")
        self.assertEqual(resolve(url).func, post_view)

    # def test_detail_url_is_resolved(self):
    #     url = reverse("post-detail")
    #     self.assertEquals(resolve(url).func, detail_view, self.post.id)

    def test_create_url_is_resolved(self):
        url = reverse("post-create")
        self.assertEqual(resolve(url).func, create_view)
