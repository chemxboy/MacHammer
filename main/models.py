from django.db import models

class Configuration(models.Model):
	sus_url = models.URLField(verbose_name=u'Software Update Server', 
		null=True, blank=True)

	gsx_sold_to = models.CharField(max_length=6, null=True, blank=True)
	gsx_ship_to = models.CharField(max_length=6, null=True, blank=True)
	gsx_username = models.CharField(max_length=64, null=True, blank=True)
	gsx_password = models.CharField(max_length=64, null=True, blank=True)

class Task(models.Model):
	title = models.CharField(max_length=255, default='New Script')
	command = models.TextField(default='#! /bin/sh\n')

class Workflow(models.Model):
	title = models.CharField(max_length=255)
	tasks = models.ManyToManyField(Task)

class Spec(models.Model):
	CATEGORIES = (
		('desktops', 'Desktops'),
		('notebooks', 'Notebooks'),
		('servers', 'Servers'),
		('devices', 'Devices'),)

	category = models.CharField(max_length=32, choices=CATEGORIES)

	title = models.CharField(max_length=255)
	model_id = models.CharField(max_length=32, blank=True, null=True)
	introduced = models.DateField(blank=True, null=True)
	discontinued = models.DateField(blank=True, null=True)
	model_number = models.CharField(max_length=32, blank=True, null=True)
	order_number = models.CharField(max_length=255, blank=True, null=True)
	photo = models.ImageField(upload_to="photos", blank=True, null=True)

	cpu = models.CharField(max_length=255, blank=True, null=True)
	cpu_speed = models.CharField(max_length=255, blank=True, null=True)
	cpu_arch = models.CharField(max_length=32, blank=True, null=True)
	cpu_cores = models.CharField(max_length=32, blank=True, null=True)
	cpu_cache = models.CharField(max_length=32, blank=True, null=True)
	cpu_bus = models.CharField(max_length=32, blank=True, null=True)

	storage = models.CharField(max_length=255, blank=True, null=True)
	storage_media = models.CharField(max_length=255, blank=True, null=True)

	original_os = models.CharField(max_length=255, blank=True, null=True)
	later_os = models.CharField(max_length=255, blank=True, null=True)
	max_os = models.CharField(max_length=255, blank=True, null=True)
	aht_version = models.CharField(max_length=255, blank=True, null=True)
	asd_version = models.CharField(max_length=255, blank=True, null=True)

	ram_builtin = models.CharField(max_length=255, blank=True, null=True)
	ram_max = models.CharField(max_length=255, blank=True, null=True)
	ram_slots = models.CharField(max_length=255, blank=True, null=True)

	gpu = models.CharField(max_length=255, blank=True, null=True)
	gpu_ram = models.CharField(max_length=255, blank=True, null=True)
	display_connection = models.CharField(max_length=255, blank=True, null=True)

	notes = models.CharField(max_length=255, blank=True, null=True)

	def get_absolute_url(self):
		return "/specs/%d/" % self.pk

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
	mac_address = models.CharField(max_length=17)
	profile = models.FileField(upload_to="profiles")

class MacProperty(ResourceProperty):
	mac = models.ForeignKey(Mac)
