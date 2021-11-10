# Generated by Django 3.2.7 on 2021-11-04 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CurieToCommonName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('curie', models.CharField(max_length=35)),
            ],
        ),
        migrations.CreateModel(
            name='GeneToPathway',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gene_curie', models.CharField(max_length=35)),
                ('pathway_curie', models.CharField(max_length=35)),
                ('p_value', models.CharField(max_length=35)),
            ],
        ),
        migrations.CreateModel(
            name='PathwayToGene',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pathway_curie', models.CharField(max_length=35)),
                ('gene_curie', models.CharField(max_length=35)),
                ('p_value', models.CharField(max_length=35)),
            ],
        ),
    ]
