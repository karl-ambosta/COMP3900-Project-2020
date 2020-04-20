# Generated by Django 3.0.3 on 2020-04-20 02:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0014_auto_20200419_1713'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderlist',
            name='status',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Active'), (2, 'Received'), (3, 'Preparing'), (4, 'Cooking'), (5, 'Pickup ready'), (6, 'Served'), (7, 'Awaiting Payment'), (8, 'Paid')], default=1),
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_number', models.IntegerField()),
                ('in_use', models.BooleanField(default=False)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tables', to='customer.Restaurant')),
            ],
        ),
    ]
