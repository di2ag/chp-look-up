from django.db import models

# Create your models here.

class GeneToPathway(models.Model):
    gene_curie = models.CharField(max_length=35)
    pathway_curie = models.CharField(max_length=35)
    p_value = models.CharField(max_length=35)

    def get_result(self):
         return self.pathway_curie, self.p_value
class PathwayToGene(models.Model):
    pathway_curie = models.CharField(max_length=35)
    gene_curie = models.CharField(max_length=35)
    p_value = models.CharField(max_length=35)

    def get_result(self) -> list:
        return self.gene_curie, self.p_value 

class CurieToCommonName(models.Model):
    curie = models.CharField(max_length=35)
    #commonName = ArrayField(models.CharField(max_length=100))
