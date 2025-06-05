from django.db import migrations
from django.utils import timezone

def publish_valid_posts(apps, schema_editor):
    Post = apps.get_model("blog", "Post")
    for post in Post.objects.select_related("category").all():
        if post.pub_date <= timezone.now() and post.category and post.category.is_published:
            post.is_published = True
            post.save(update_fields=["is_published"])

class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(publish_valid_posts),
    ]