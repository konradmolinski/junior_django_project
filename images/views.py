import pytz
import datetime
import magic
from io import BytesIO
from PIL import Image as pil_img
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from images.models import Image, Thumbnail, BinaryImage
from .serializers import ImageSerializer


class PostImageAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):

        if not request.FILES:
            return Response({"error_msg": "No image in request.FIlES."}, status=400)

        data_key = list(request.FILES.keys())[0]
        uploaded_image = request.FILES[data_key]

        if uploaded_image.size > settings.MAXIMUM_IMAGE_SIZE:
            return Response({"error_msg": "File size is too big."}, status=400)

        mime = magic.Magic(mime=True)
        mimetype = mime.from_buffer(uploaded_image.file.read(2048))
        uploaded_image.file.seek(0)

        if mimetype not in settings.VALID_IMAGE_MIMETYPES:
            return Response({"error_msg": "Wrong file format."}, status=400)

        account = request.user.account
        image = Image(image=uploaded_image, account=account)
        image.save()

        thumbnail_list = []
        for thumbnail_height in account.tier.thumbnail_sizes:

            pil_image = pil_img.open(uploaded_image)
            width, height = pil_image.size

            thumbnail_width = int(width/(height/thumbnail_height))
            pil_image.thumbnail((thumbnail_width, thumbnail_height))
            buffer = BytesIO()
            pil_image.save(fp=buffer, format=uploaded_image.name.split('.')[1])

            thumbnail_image = SimpleUploadedFile(f"{thumbnail_width}x{thumbnail_height}_thumbnail_{uploaded_image.name}",
                                                 buffer.getvalue(), content_type=mimetype)

            thumbnail = Thumbnail(original_image=image, thumbnail=thumbnail_image)
            thumbnail.save()
            thumbnail_list.append(settings.HOSTNAME + thumbnail.thumbnail.url)

        original_image_pk = image.pk
        if account.tier.original_image_link_bool:

            original_image_url = settings.HOSTNAME + image.image.url
            return Response({'thumbnails': thumbnail_list, 'original_image_url': original_image_url,
                             'expiring_link': account.tier.expiring_link_bool, 'original_image_pk': original_image_pk})

        else:
            return Response({'thumbnails': thumbnail_list, 'expiring_link': account.tier.expiring_link_bool,
                             'original_image_pk': original_image_pk})


class GetUsersImagesAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):

        account = request.user.account
        paginator = PageNumberPagination()
        queryset = Image.objects.filter(account=account).order_by('id')
        context = paginator.paginate_queryset(queryset, request)
        serializer = ImageSerializer(context, many=True)

        return paginator.get_paginated_response(serializer.data)


class ExpirationLinkAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):

        original_image_pk = request.data['original_image_pk']
        original_image = Image.objects.filter(pk=original_image_pk).get()

        if BinaryImage.objects.filter(original_image=original_image).exists():
            return Response({"error_msg": "Expiration link already fetched."}, status=400)

        expiration_time = int(request.data['expiration_time'])
        if not 300 <= expiration_time <= 30000:
            return Response({"error_msg": "Wrong expiration time value."}, status=400)

        try:
            pil_image = pil_img.open(f'{settings.BASE_DIR}{original_image.image.url}')
        except:
            pil_image = pil_img.open(f'{settings.BASE_DIR}/test_data{original_image.image.url}')

        pil_image = pil_image.convert('L')
        threshold = 100
        pil_image = pil_image.point(lambda p: 255 if p > threshold else 0)
        pil_image = pil_image.convert('1')

        buffer = BytesIO()
        pil_image.save(fp=buffer, format='png')

        binary_image_file = SimpleUploadedFile(f"binary_{original_image.image.name.split('.')[0]}.png",
                                      buffer.getvalue(), content_type='image/png')

        timezone = pytz.timezone(settings.TIME_ZONE)
        expiration_date = timezone.localize(datetime.datetime.now() + datetime.timedelta(seconds=expiration_time))

        binary_image = BinaryImage(binary_image=binary_image_file, expiration_date=expiration_date,
                                   original_image=original_image)
        binary_image.save()
        expiring_link = settings.HOSTNAME + binary_image.binary_image.url

        return Response({'expiring_link': expiring_link})
