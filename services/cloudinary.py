"""
Cloudinary Service Module
-------------------------
This module provides integration with the Cloudinary service for managing 
image uploads, transformations, and generating public URLs for user avatars.
"""

import cloudinary
import cloudinary.uploader
from config.config import settings

class CloudinaryService:
    """
    Service class for interacting with the Cloudinary API.
    Handles configuration and image processing operations.
    """
    def __init__(self):
        """
        Initializes the Cloudinary configuration using settings from the application config.
        Sets cloud name, API key, API secret, and forces secure (HTTPS) connections.
        """
        cloudinary.config(
            cloud_name=settings.cloudinary_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
            secure=True
        )

    def upload_image(self, file, public_id: str):
        """
        Uploads an image file to Cloudinary and returns a transformed URL.

        The image is overwritten if the public_id already exists. The returned 
        URL points to a version of the image cropped to a 250x250 square using 
        the 'fill' method.

        :param file: The file-like object or path to the image to be uploaded.
        :type file: Any
        :param public_id: The unique identifier (path) for the image in Cloudinary.
        :type public_id: str
        :return: A secure URL to the transformed image.
        :rtype: str
        """
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop='fill', version=r.get('version')
        )
        return src_url

cloudinary_service = CloudinaryService()