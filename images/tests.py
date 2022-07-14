import shutil
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from django.test import override_settings
from django.conf import settings
from .models import Image, Account, Tier, Thumbnail
from rest_framework.authtoken.models import Token
from PIL import Image as im
from io import BytesIO

TEST_DIR = 'test_data'
client = Client()


def create_user_account(username, password):
    user = User(username=username)
    user.set_password(password)
    user.save()
    return user


class PostImageTestCase(TestCase):
    fixtures = ['tier_fixtures.json']

    def setUp(self):

        self.user = create_user_account(username='user1', password='123')
        self.user_password = '123'

        self.assertTrue(Account.objects.all().exists())
        self.assertTrue(Token.objects.all().exists())

        self.user.account.tier = Tier.objects.filter(pk=1).get()
        self.user.account.save()
        self.assertEqual(len(self.user.account.tier.thumbnail_sizes), 1)

        response = client.post('/api/token-auth', {"username": self.user.username, "password": self.user_password})

        self.assertTrue(response.json()['token'])
        self.token = response.json()['token']

    @override_settings(MEDIA_ROOT=(settings.BASE_DIR/'media'/TEST_DIR))
    def test_valid_jpg_post(self):

        im_obj = im.new(mode="RGB", size=(200, 200))
        buffer = BytesIO()
        im_obj.save(fp=buffer, format='JPEG')

        img_file = SimpleUploadedFile("test_img.jpg", buffer.getvalue(), content_type='image/jpg')

        response = client.post('/api/post-image', {'image': img_file}, HTTP_AUTHORIZATION='Token ' + self.token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Image.objects.all().exists())
        self.assertTrue(Thumbnail.objects.filter(thumbnail__isnull=False).exists())

    @override_settings(MEDIA_ROOT=(settings.BASE_DIR/'media'/TEST_DIR))
    def test_valid_png_post(self):

        im_obj = im.new(mode="RGB", size=(200, 200))
        buffer = BytesIO()
        im_obj.save(fp=buffer, format='PNG')

        img_file = SimpleUploadedFile("test_image.png", buffer.getvalue(), content_type='image/png')

        response = client.post('/api/post-image', {'image': img_file}, HTTP_AUTHORIZATION='Token ' + self.token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Image.objects.all().exists())
        self.assertTrue(Thumbnail.objects.filter(thumbnail__isnull=False).exists())

        print(response.json())

    @override_settings(MAXIMUM_IMAGE_SIZE=100)
    def test_image_size_in_bytes_validation(self):

        im_obj = im.new(mode="RGB", size=(200, 200))
        buffer = BytesIO()
        im_obj.save(fp=buffer, format='JPEG')

        img_file = SimpleUploadedFile("test_img.jpg", buffer.getvalue(), content_type='image/jpg')

        response = client.post('/api/post-image', {'image': img_file}, HTTP_AUTHORIZATION='Token ' + self.token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error_msg'], "File size is too big.")

    def test_invalid_image_format_post(self):

        im_obj = im.new(mode="RGB", size=(200, 200))
        buffer = BytesIO()
        im_obj.save(fp=buffer, format='GIF')

        img_file = SimpleUploadedFile("test_image.gif", buffer.getvalue(), content_type='image/gif')

        response = client.post('/api/post-image', {'image': img_file}, HTTP_AUTHORIZATION='Token ' + self.token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error_msg'], "Wrong file format.")

    def test_post_without_file(self):

        response = client.post('/api/post-image', HTTP_AUTHORIZATION='Token ' + self.token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error_msg'], "No image in request.FIlES.")


def tearDownModule():
    try:
        shutil.rmtree('media/'+TEST_DIR)
    except OSError:
        pass