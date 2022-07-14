from rest_framework import viewsets
from rest_framework.response import Response
from images.models import Image, Thumbnail
import magic
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as im
from io import BytesIO


class PostImageAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):

        if not request.FILES:
            return Response({"error_msg": "No image in request.FIlES."}, status=400)

        data_key = list(request.FILES.keys())[0]
        image = request.FILES[data_key]

        if image.size > settings.MAXIMUM_IMAGE_SIZE:
            return Response({"error_msg": "File size is too big."}, status=400)

        mime = magic.Magic(mime=True)
        mimetype = mime.from_buffer(image.file.read(2048))
        image.file.seek(0)

        if mimetype not in settings.VALID_IMAGE_MIMETYPES:
            return Response({"error_msg": "Wrong file format."}, status=400)

        account = request.user.account
        img = Image(image=image, account=account)
        img.save()

        thumbnail_list = []
        for thumbnail_height in account.tier.thumbnail_sizes:

            im_obj = im.open(image)
            width, height = im_obj.size

            thumbnail_width = int(width/(height/thumbnail_height))
            im_obj.thumbnail((thumbnail_width, thumbnail_height))
            buffer = BytesIO()
            im_obj.save(fp=buffer, format=mimetype[6:])

            img_file = SimpleUploadedFile(f"{thumbnail_width}x{thumbnail_height}_thumbnail_{request.FILES[data_key].name}",
                                          buffer.getvalue(), content_type=mimetype)

            thumbnail = Thumbnail(image=img, thumbnail=img_file)
            thumbnail.save()
            thumbnail_list.append(settings.HOSTNAME + thumbnail.thumbnail.url)

        if account.tier.original_file_link:

            original_image_url = settings.HOSTNAME + img.image.url
            return Response({'thumbnails': thumbnail_list, 'original_image_url': original_image_url,
                             'expiring_link': account.tier.expiring_links})

        else:
            return Response({'thumbnails': thumbnail_list, 'expiring_link': account.tier.expiring_links})
