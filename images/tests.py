import shutil
from PIL import Image as pil_img
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from django.test import override_settings
from django.conf import settings
from rest_framework.authtoken.models import Token
from .models import Image, Account, Tier, Thumbnail, BinaryImage



TEST_DIR = 'test_data'
client = Client()


def create_user_account(username, password):
    user = User(username=username)
    user.set_password(password)
    user.save()
    return user


def create_and_post_image(extension, content_type, token):
    im_obj = pil_img.new(mode="RGB", size=(200, 200))
    buffer = BytesIO()
    im_obj.save(fp=buffer, format=extension)

    img_file = SimpleUploadedFile("test_img." + extension.lower(), buffer.getvalue(), content_type=content_type)
    response = client.post('/api/post-image', {'image': img_file}, HTTP_AUTHORIZATION='Token ' + token)
    return response


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

    @override_settings(MEDIA_ROOT=(settings.BASE_DIR/TEST_DIR/'media'))
    def test_valid_jpg_post(self):

        response = create_and_post_image('JPEG', 'image/jpeg', self.token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Image.objects.all().exists())
        self.assertTrue(Thumbnail.objects.filter(thumbnail__isnull=False).exists())

    @override_settings(MEDIA_ROOT=(settings.BASE_DIR/TEST_DIR/'media'))
    def test_valid_png_post(self):

        response = create_and_post_image('PNG', 'image/png', self.token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Image.objects.all().exists())
        self.assertTrue(Thumbnail.objects.filter(thumbnail__isnull=False).exists())

    @override_settings(MAXIMUM_IMAGE_SIZE=100)
    def test_image_size_in_bytes_validation(self):

        response = create_and_post_image('JPEG', 'image/jpeg', self.token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error_msg'], "File size is too big.")

    def test_invalid_image_format_post(self):

        response = create_and_post_image('GIF', 'image/gif', self.token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error_msg'], "Wrong file format.")

    def test_post_without_file(self):

        response = client.post('/api/post-image', HTTP_AUTHORIZATION='Token ' + self.token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error_msg'], "No image in request.FIlES.")


class GetListOfImagesTestCase(TestCase):
    fixtures = ['tier_fixtures.json']

    @override_settings(MEDIA_ROOT=(settings.BASE_DIR/TEST_DIR/'media'))
    def setUp(self):

        self.user = create_user_account(username='user1', password='123')
        self.user_password = '123'

        self.user.account.tier = Tier.objects.filter(pk=1).get()
        self.user.account.save()

        response = client.post('/api/token-auth', {"username": self.user.username, "password": self.user_password})

        self.token = response.json()['token']

        for i in range(10):
            create_and_post_image('JPEG', 'image/jpeg', self.token)

    def test_getting_users_images(self):

        response = client.get('/api/get-users-images', HTTP_AUTHORIZATION='Token ' + self.token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), settings.REST_FRAMEWORK['PAGE_SIZE'])


class ExpirationLinkTestCase(TestCase):
    fixtures = ['tier_fixtures.json']

    @override_settings(MEDIA_ROOT=(settings.BASE_DIR/TEST_DIR/'media'))
    def setUp(self):

        self.user = create_user_account(username='user1', password='123')
        self.user_password = '123'

        self.user.account.tier = Tier.objects.filter(pk=3).get()
        self.user.account.save()

        response = client.post('/api/token-auth', {"username": self.user.username, "password": self.user_password})
        self.token = response.json()['token']

        response = create_and_post_image('JPEG', 'image/jpeg', self.token)
        self.original_image_pk = response.json()['original_image_pk']

    def test_invalid_expiration_time_value(self):

        response = client.post('/api/expiration-link', {'original_image_pk': self.original_image_pk,
                                                        'expiration_time': 200}, HTTP_AUTHORIZATION='Token ' + self.token)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error_msg'], "Wrong expiration time value.")

    @override_settings(MEDIA_ROOT=(settings.BASE_DIR / TEST_DIR / 'media'))
    def test_getting_expiration_link(self):

        response = client.post('/api/expiration-link', {'original_image_pk': self.original_image_pk,
                                                        'expiration_time': 300}, HTTP_AUTHORIZATION='Token ' + self.token)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(BinaryImage.objects.all().exists())

        response = client.post('/api/expiration-link', {'original_image_pk': self.original_image_pk,
                                                        'expiration_time': 300}, HTTP_AUTHORIZATION='Token ' + self.token)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error_msg'], "Expiration link already fetched.")

def tearDownModule():
    try:
        shutil.rmtree(TEST_DIR + '/media')
    except OSError:
        pass