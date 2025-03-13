from celery import celery
from PIL import Image
import os,cloudinary.uploader

def process_image_task(temp_filepath,user_id):
    pass