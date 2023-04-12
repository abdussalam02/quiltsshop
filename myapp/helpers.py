from django.utils.text import slugify
import string, random
    
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