import os
import uuid
from django.db import models

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile



def get_image_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('predict', 'images', filename)


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ("Male", _("Male")),
        ("Female", _("Female")),
        ("Other", _("Other")),
    ]
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee',
        null=True,
        blank=True
    )
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    gender = models.CharField(
        max_length=8,
        default="Other",
        choices=GENDER_CHOICES
    )
    phone = models.CharField(max_length=64, blank=True, null=True)
    address = models.CharField(max_length=256, blank=True, null=True)
    date_created = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        null=True
    )
    date_modified = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True
    )
    objects = models.Manager()


    def __str__(self):
        return self.user.username
 

class Predict(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predict')
    image = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    thumbnail = models.ImageField(upload_to=get_image_path, editable=False, null=True, blank=True)
    PREDICTIONS = [
        ("healthy", _("healthy"),),
        ("leafblast", _("leafblast"),),
        ("brownspot", _("brownspot"),),
        ("blight", _("blight"),),
    ]
    prediction = models.CharField(
        max_length=16,
        default='healthy',
        choices=PREDICTIONS,
    )
    confidence = models.CharField(max_length=8, null=True, blank=True)
    date_created = models.DateTimeField(
        auto_now_add=True,
        blank=True,
    )

    def make_thumbnail(self):
        try:
            image = Image.open(self.image)
            image.thumbnail((256, 256), Image.ANTIALIAS)
            thumb_name, thumb_extension = os.path.splitext(self.image.name)
            thumb_extension = thumb_extension.lower()
            thumb_filename = thumb_name + '_thumb' + thumb_extension
            if thumb_extension in ['.jpg', '.jpeg']:
                FTYPE = 'JPEG'
            elif thumb_extension == '.gif':
                FTYPE = 'GIF'
            elif thumb_extension == '.png':
                FTYPE = 'PNG'
            else:
                return False  # Unrecognized file type
            # Save thumbnail to in-memory file as StringIO
            temp_thumb = BytesIO()
            image.save(temp_thumb, FTYPE)
            temp_thumb.seek(0)
            # set save=False, otherwise it will run in an infinite loop
            self.thumbnail.save(thumb_filename, ContentFile(
                temp_thumb.read()), save=False)
            temp_thumb.close()
            return True
        except:
            pass

    def save(self, *args, **kwargs):
        if not self.thumbnail:
            self.make_thumbnail()

        return super(Predict, self).save(*args, **kwargs)


    def __str__(self) -> str:
        return self.prediction
