from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class RepairType(models.Model):
    repair_type = models.CharField(max_length=20)
    def __str__(self):
        return f"{self.repair_type}"
    
class PartType(models.Model):
    part_type = models.CharField(max_length=20)
    def __str__(self):
        return f"{self.part_type}"
    
class DC(models.Model):
    dc = models.IntegerField(unique=True)
    def __str__(self):
        return f"{self.dc}"
    
class Associate(models.Model):
    associate = models.CharField(max_length=30, unique=True)
    dc = models.ForeignKey(DC, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.associate} - {self.dc}"

class PointPiece(models.Model):
    associate = models.ForeignKey(Associate, on_delete=models.CASCADE, null=True, blank=True)
    sku = models.PositiveSmallIntegerField(blank=True)
    lp = models.CharField(max_length=25 ,blank=True)
    route = models.CharField(max_length=3, blank=True)
    dc = models.ForeignKey(DC, on_delete=models.CASCADE, null=True, blank=True)
    STOCK_TYPE_CHOICES = [
        ('New', 'N'),
        ('Repaired in Shop', 'D'),
        ('Merchandise Returns', 'R'),
        ('Clearance Item', 'C'),
    ]
    stock_type = models.CharField(max_length=20, choices=STOCK_TYPE_CHOICES)
    STATUS_CHOICES = [
        ('Repair In Progress', 'Repair In Progress'),
        ('Repair Complete', 'Repair Complete'),
    ]
    
    line_time = models.DateTimeField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    repair = models.ManyToManyField(RepairType)
    part = models.ManyToManyField(PartType)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='Repair In Progress')

    def save(self, *args, **kwargs):
        # If status is 'Repair Complete', set end_time to current time
        if self.status == 'Repair Complete' and self.end_time is None:
            self.end_time = timezone.now()
        super(PointPiece, self).save(*args, **kwargs)

    def time_to_repair(self):
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            total_minutes = duration.total_seconds() / 60  # Convert duration to minutes
            return f"{int(total_minutes)} minutes"
        else:
            return "N/A"


    def __str__(self):
        return f"{self.sku} - {self.lp} - {self.route} - {self.associate}"
    
class Route(models.Model):
    route = models.CharField(max_length=3, unique=True)
    def __str__(self):
        return f"{self.route}"