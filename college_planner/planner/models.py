from django.db import models

# Create your models here.
class Research(models.Model):
    professor_name = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    website = models.CharField(max_length=255)
    research_interest = models.CharField(max_length=255)
    src_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.professor_name