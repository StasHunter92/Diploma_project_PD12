# Generated by Django 4.1.7 on 2023-04-17 17:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("goals", "0007_create_new_objects"),
    ]

    operations = [
        migrations.AlterField(
            model_name="goalcategory",
            name="board",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="goals.board",
                verbose_name="Доска",
            ),
        ),
    ]
