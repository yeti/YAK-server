import StringIO
import os
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
# from yak.rest_core.utils import retry_cloudfiles
from model_utils import Choices


class CoreModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __repr__(self):
        return '<{}:{} {}>'.format(self.__class__.__name__, self.pk, str(self))

    class Meta:
        abstract = True


class Media(CoreModel):
    TYPE_CHOICES = Choices(
        (0, 'image', 'Image'),
        (1, 'video', 'Video')
    )
    media_type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, blank=True, null=True)
    original_file = models.FileField(upload_to='media/original/', blank=True, null=True)
    thumbnail = models.FileField(upload_to='media/thumbnail/', blank=True, null=True)
    large_photo = models.FileField(upload_to='media/large_photo/', blank=True, null=True)
    original_file_name = "original_file"

    class Meta:
        abstract = True


def resize_model_photos(obj):
    """
    Requires the model to have one field to hold the original file and a constant called SIZES
    Expects the sender to have an attribute `original_file` or to define an alternate with `original_file_name`
    """
    original_file_field_name = getattr(obj, "original_file_name", "original_file")

    # If this is a video file, do nothing
    file_type = getattr(obj, "media_type", None)
    if file_type and file_type == obj.TYPE_CHOICES.video:
        return

    original_file = getattr(obj, original_file_field_name)
    if not original_file:
        for size_name, size in obj.SIZES.iteritems():
            setattr(obj, size_name, '')
        return

    process_thumbnail(obj, original_file, obj.SIZES)


def process_thumbnail(instance, original_file, sizes, crop=False):
    """
    Makes a smart thumbnail
    """
    # TODO: All of this is terrible
    try:
        file = StringIO.StringIO(original_file.read())
        file.seek(0)
        original_image = Image.open(file)  # open the image using PIL
    except IOError:
        # Open the file because this takes care of `seek(0)` but is more flexible
        # When the original photo has already been saved and `save` is called more than once in a view,
        # this block will execute
        file = StringIO.StringIO(open(original_file.path, 'r').read())
        original_image = Image.open(file)  # open the image using PIL

    original_file.seek(0)

    # pull a few variables out of that full path
    filename = os.path.basename(original_file.name).rsplit('.', 1)[0]
    extension = os.path.basename(original_file.name).rsplit('.', 1)[1]  # the file extension

    # If there is no extension found try jpg
    if extension == '':
        extension = 'jpg'

    # use the file extension to determine if the image is valid before proceeding
    if extension not in ['jpg', 'jpeg', 'gif', 'png']:
        return False

    for size_name, size in sizes.iteritems():
        im = original_image.copy()

        (x_size, y_size) = im.size
        original_ratio = float(x_size) / float(y_size)
        width = size['width']
        height = size['height']
        new_ratio = float(width / height)
        if new_ratio > original_ratio:
            im = im.resize((width, int(width / original_ratio)), Image.ANTIALIAS)
            if crop:
                clip_amount = int((int(width / original_ratio) - height) / 2)
                im = im.crop((0, clip_amount, width, height + clip_amount))
        else:
            im = im.resize((int(height * original_ratio), height), Image.ANTIALIAS)
            if crop:
                clip_amount = int((int(height * original_ratio) - width) / 2)
                im = im.crop((clip_amount, 0, width + clip_amount, height))

        name = "{}.jpg".format(filename)
        tempfile_io = StringIO.StringIO()
        if im.mode != "RGB":
            im = im.convert("RGB")
        im.save(tempfile_io, 'JPEG')

        temp_file = InMemoryUploadedFile(tempfile_io, None, name, 'image/jpeg', tempfile_io.len, None)
        temp_file.seek(0)
        setattr(instance, size_name, temp_file)

        # def save_image(temp_file, instance, size_name, name):
        #     # Make sure we're at the beginning of the file for reading when saving
        #     temp_file.seek(0)
        #     instance.update(**{size_name: temp_file})
        #
        # retry_cloudfiles(save_image, temp_file, instance, size_name, name)

    return True
