import base64
from rest_framework.test import RequestsClient
from django.conf import settings
from django.test import TestCase


client = RequestsClient()


def send_request(url, data):
    return client.post(url="http://localhost:8000/api/" + url, json=data)


class PostImageTestCase(TestCase):

    def test_jpeg_image_posting(self):

        img_path = settings.BASE_DIR/'media/test_images/Kitten-Blog.jpeg/'

        with open(img_path, 'rb') as f:
            image = base64.b64encode(f.read()).decode('utf-8')

        response = send_request(url='post-image', data={'image': image})
        self.assertEqual(response.status_code, 200)

