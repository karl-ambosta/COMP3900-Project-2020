# Generated by Django 3.0.3 on 2020-03-30 08:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0004_remove_orderlist_menuitems'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderrequest',
            name='menu_item',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='order_request', to='customer.MenuItem'),
            preserve_default=False,
        ),
    ]
