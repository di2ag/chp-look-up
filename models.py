from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class GeneToPathway(models.Model):
    gene = models.CharField(max_length=35, primary_key=True)
    pathways = ArrayField(models.CharField(max_length=35))

    def get_result(self) -> list:
        return self.pathways

class PathwayToGene(models.Model):
    pathway = models.CharField(max_length=35, primary_key=True)
    genes = ArrayField(models.CharField(max_length=35))

    def get_result(self) -> list:
        return self.genes