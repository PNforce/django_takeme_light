# Generated by Django 2.1 on 2020-06-30 09:18

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(max_length=200)),
                ('text', models.TextField()),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=64, null=True)),
                ('startloc', models.CharField(max_length=64)),
                ('endloc', models.CharField(max_length=64)),
                ('starttime', models.CharField(max_length=64)),
                ('endtime', models.CharField(max_length=64)),
                ('price', models.CharField(max_length=20)),
                ('desc', models.TextField(max_length=200)),
                ('file', models.ImageField(upload_to='')),
                ('state', models.CharField(max_length=20)),
                ('owner', models.CharField(max_length=20)),
                ('accepter', models.CharField(max_length=20)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=200, null=True)),
                ('last_name', models.CharField(max_length=200, null=True)),
                ('email', models.CharField(max_length=200, null=True)),
                ('username', models.CharField(max_length=200, null=True)),
                ('password', models.CharField(max_length=200, null=True)),
                ('activate', models.CharField(max_length=200, null=True)),
                ('bday', models.DateField(null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('activated', models.BooleanField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='forum.QuestionPost'),
        ),
    ]
