from django.db import models
from django.conf import settings
from apps.marketplace.models import Category

class FreelanceProject(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects_created")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Proposal(models.Model):
    project = models.ForeignKey(FreelanceProject, on_delete=models.CASCADE, related_name="proposals")
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="proposals_sent")
    cover_letter = models.TextField()
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_days = models.PositiveIntegerField()
    
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proposal for {self.project.title} by {self.freelancer.email}"

class Milestone(models.Model):
    project = models.ForeignKey(FreelanceProject, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} - {self.amount}"
