from django.db import models

class Configuration(models.Model):
	sus_url = models.URLField(verbose_name=u'Software Update Server', null=True, blank=True)

class Task(models.Model):
	title = models.CharField(max_length=255)
	command = models.CharField(max_length=255)

class Workflow(models.Model):
	title = models.CharField(max_length=255)
	tasks = models.ManyToManyField(Task)

class Spec(models.Model):
	title = models.CharField(max_length=255)
	model_id = models.CharField(max_length=32)

class Property(models.Model):
	key = models.CharField(max_length=255)
	format = models.CharField(max_length=255)

class ResourceProperty(models.Model):
	prop = models.ForeignKey(Property)
	value = models.CharField(max_length=255)

	class Meta:
		abstract = True

class SpecProperty(ResourceProperty):
	spec = models.ForeignKey(Spec)

class Mac(models.Model):
	spec = models.ForeignKey(Spec)
	sn = models.CharField(max_length=32)

class MacProperty(ResourceProperty):
	mac = models.ForeignKey(Mac)
