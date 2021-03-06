# Generated by Django 3.1.6 on 2022-06-16 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mortgage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(max_length=50)),
                ('term_min', models.IntegerField()),
                ('term_max', models.IntegerField()),
                ('rate_min', models.FloatField()),
                ('rate_max', models.FloatField()),
                ('payment_min', models.IntegerField()),
                ('payment_max', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Калькулятор',
                'verbose_name_plural': 'Калькуляторы',
                'ordering': ('-id',),
            },
        ),
    ]
