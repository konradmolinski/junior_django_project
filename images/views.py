from rest_framework import viewsets
from rest_framework.response import Response
import imghdr
import base64


class PostImageAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        image = base64.b64decode(request.data['image'])

        if not image:
            return Response({"error_msg": "Image must be uploaded before posting."}, status=400)
        if imghdr.what('', h=image) not in ('jpeg', 'png'):
            return Response({"error_msg": "Wrong file format."}, status=400)

        return Response({'features_view_url': '#'})
