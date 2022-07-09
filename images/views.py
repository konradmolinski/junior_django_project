from rest_framework import viewsets
from rest_framework.response import Response
from django.contrib.auth.models import User
from images.models import Image, Account
from django.core.files import File
import imghdr
import base64


class PostImageAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        print('piwo')
        image = request.FILES['image'].name
        print('aha')
        print(image + 'aha')

        if not image:
            return Response({"error_msg": "Image must be uploaded before posting."}, status=400)
        if imghdr.what('', h=base64.b64decode(image)) not in ('jpeg', 'png'):
            return Response({"error_msg": "Wrong file format."}, status=400)

        account = request.user.account
        image = Image(image=image, account=account)
        image.save()

        return Response({'features_view_url': '#'})
