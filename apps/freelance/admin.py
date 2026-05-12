from django.contrib import admin
from .models import FreelanceProject, Proposal, Milestone

@admin.register(FreelanceProject)
class FreelanceProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'budget', 'status', 'deadline', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description')
    autocomplete_fields = ('client', 'category')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('client', 'category', 'title', 'description', 'budget', 'deadline', 'status')
        }),
    )

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('project', 'freelancer', 'bid_amount', 'delivery_days', 'is_accepted')
    list_filter = ('is_accepted',)
    autocomplete_fields = ('project', 'freelancer')

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'amount', 'is_paid', 'is_completed')
    autocomplete_fields = ('project',)
