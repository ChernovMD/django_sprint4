from django.db import migrations


def create_default_categories(apps, schema_editor):
    Category = apps.get_model("blog", "Category")
    Category.objects.get_or_create(
        title="Новости",
        slug="news",
        defaults={"description": "Все последние новости.", "is_published": True},
    )
    Category.objects.get_or_create(
        title="Наука",
        slug="science",
        defaults={"description": "О научных открытиях.", "is_published": True},
    )
    Category.objects.get_or_create(
        title="Путешествия",
        slug="travel",
        defaults={"description": "О новых местах.", "is_published": True},
    )


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"), 
    ]

    operations = [
        migrations.RunPython(create_default_categories),
    ]