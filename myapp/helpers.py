from django.utils.text import slugify
import string, random
from io import BytesIO
from PIL import Image
from django.core.files import File

#image compression method
def compress_img(image):
    im = Image.open(image)
    im_io = BytesIO()
    im.resize((400, 400))
    im.save(im_io, format="webp", quality=70) 
    new_image = File(im_io, name=image.name)
    return new_image
    
def generate_random_string(n):
    result = ''.join(random.choices(string.ascii_uppercase+string.digits, k=n))
    return result

def generate_slug(text):
    new_slug = slugify(text)
    from .models import ProductVariant
    if ProductVariant.objects.filter(slug=new_slug).exists():
        return generate_slug(text+generate_random_string(5))
    return new_slug

def generate_blog_slug(text):
    new_slug = slugify(text)
    from .models import Blog
    if Blog.objects.filter(slug=new_slug).exists():
        return generate_slug(text+generate_random_string(5))
    return new_slug