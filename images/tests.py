import base64
from rest_framework.test import RequestsClient
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


client = RequestsClient()

def create_user_account(username, password):
    user = User(username=username)
    user.save()
    user.set_password(password)
    user.save()
    return user


class PostImageTestCase(TestCase):

    def setUp(self):

        self.user = create_user_account(username='user1', password='123')
        self.user_password = '123'

        self.assertEqual(Token.objects.all().exists(), True)
        response = client.post("http://localhost:8000/api/token-auth", data={"username": self.user.username,
                                                                             "password": self.user_password} )

        self.token = response.json()['token']
        self.assertIsNotNone(response)

    def test_jpeg_image_posting(self):

        img_path = settings.BASE_DIR/'media/test_images/Kitten-Blog.jpeg/'

        with open(img_path, 'rb') as f:
            image = base64.b64encode(f.read()).decode('utf-8')

        response = client.post(url='http://localhost:8000/api/post-image', data={'image': image},
                               headers={'Authorization': 'Token ' + self.token})

        self.assertEqual(response.status_code, 200)

