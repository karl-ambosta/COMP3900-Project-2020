# Generated by Django 3.0.3 on 2020-03-24 04:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('menuItems', models.ManyToManyField(related_name='ordered_by', to='customer.MenuItem')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_list', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
