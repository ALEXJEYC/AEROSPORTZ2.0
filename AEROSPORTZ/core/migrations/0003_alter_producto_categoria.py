# Generated by Django 4.2.2 on 2023-06-28 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_carrito_categoria_remove_producto_nombre_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='categoria',
            field=models.CharField(default='Sin categoría', max_length=100),
        ),
    ]
