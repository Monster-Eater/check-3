"""Cloudinary storage that remembers the detected resource type in the field name.

django-cloudinary-storage's auto resource type is valid for uploads, but the
delivery URL must use the detected type (image, video, or raw). This storage
encodes that type alongside the public ID so later URL generation is reliable.
"""

import os

import cloudinary
import cloudinary.uploader
from django.core.files.uploadedfile import UploadedFile
from cloudinary_storage.storage import MediaCloudinaryStorage


class AutoResourceCloudinaryStorage(MediaCloudinaryStorage):
    marker = "::"

    def _upload(self, name, content):
        options = {
            "use_filename": True,
            "resource_type": "auto",
            "tags": self.TAG,
        }
        folder = os.path.dirname(name)
        if folder:
            options["folder"] = folder
        return cloudinary.uploader.upload(content, **options)

    def _save(self, name, content):
        name = self._normalise_name(name)
        name = self._prepend_prefix(name)
        content = UploadedFile(content, name)
        response = self._upload(name, content)
        resource_type = response.get("resource_type", "image")
        public_id = response["public_id"]
        extension = os.path.splitext(name)[1].lower()
        if not extension and response.get("format"):
            extension = f".{response['format'].lower()}"
        return f"{resource_type}|{extension}{self.marker}{public_id}"

    def _split_name(self, name):
        if self.marker in name:
            metadata, public_id = name.split(self.marker, 1)
            resource_type, separator, extension = metadata.partition("|")
            if resource_type in {"image", "video", "raw"}:
                return resource_type, public_id, extension if separator else ""

        # Files saved before this storage was installed were uploaded with
        # auto detection but their type was not retained. Existing reported
        # picture uploads are therefore delivered as images by default.
        extension = os.path.splitext(name)[1].lower()
        basename = os.path.basename(name).lower()
        if extension in {".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi", ".mp3", ".m4a", ".wav", ".ogg", ".aac", ".opus"}:
            return "video", name, extension
        if basename.startswith("voice_"):
            return "video", name, ".m4a"
        if basename.startswith(("vid_", "video_")):
            return "video", name, ".mp4"
        if "/video/" in name.lower():
            return "video", name, ".mp4"
        if extension and extension not in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".heic", ".heif"}:
            return "raw", name, extension
        return "image", name, extension

    def _get_resource_type(self, name):
        return self._split_name(name)[0]

    def _get_url(self, name):
        resource_type, public_id, _ = self._split_name(name)
        return cloudinary.CloudinaryResource(
            public_id,
            default_resource_type=resource_type,
        ).url

    def url_for_resource_type(self, name, resource_type):
        """Build an explicit URL when the Django field itself defines the type."""
        _, public_id, _ = self._split_name(name)
        if resource_type not in {"image", "video", "raw"}:
            resource_type = self._get_resource_type(name)
        return cloudinary.CloudinaryResource(
            public_id,
            default_resource_type=resource_type,
        ).url

    def delete(self, name):
        resource_type, public_id, _ = self._split_name(name)
        response = cloudinary.uploader.destroy(
            public_id,
            invalidate=True,
            resource_type=resource_type,
        )
        return response.get("result") == "ok"
