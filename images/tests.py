import base64
import tempfile
from PIL import Image
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


def temporary_image():
    image = Image.new('RGB', (100, 100))
    tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg', prefix='test_img_')
    image.save(tmp_file, 'jpeg')
    tmp_file.seek(0)
    return tmp_file


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

        # img_path = settings.BASE_DIR/'media/test_images/Kitten-Blog.jpeg/'
        # with open(img_path, 'rb') as f:
        #     image = base64.b64encode(f.read()).decode('utf-8')

        response = client.post(url='http://localhost:8000/api/post-image', data={'image': temporary_image()},
                               headers={'Authorization': 'Token ' + self.token, 'Content-Type': 'multipart/form-data'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Image.objects.all().exists(), True)

