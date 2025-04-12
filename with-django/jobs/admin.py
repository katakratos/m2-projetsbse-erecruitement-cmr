from django.contrib import admin
from .models import Job, Criteria, Candidates, AHPPriority,CandidateData

# Register Job model with customizations
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'location', 'type', 'deadline', 'created_at')
    list_filter = ('type', 'location', 'created_at')
    search_fields = ('title', 'description', 'employer__company_name')
    date_hierarchy = 'created_at'

# Register Criteria model
@admin.register(Criteria)
class CriteriaAdmin(admin.ModelAdmin):
    list_display = ('criteria', 'job')
    list_filter = ('job',)
    search_fields = ('criteria', 'job__title')

# Register Candidates model
@admin.register(Candidates)
class CandidatesAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'ahp_rank', 'final_score')
    list_filter = ('job',)
    search_fields = ('user__username', 'job__title')

# Register AHPPriority model
@admin.register(AHPPriority)
class AHPPriorityAdmin(admin.ModelAdmin):
    list_display = ('job', 'consistency_ratio', 'is_consistent', 'created_at', 'updated_at')
    list_filter = ('is_consistent',)
    search_fields = ('job__title',)
    readonly_fields = ('consistency_ratio', 'is_consistent', 'created_at', 'updated_at')
    
    def has_delete_permission(self, request, obj=None):
        # Prevent accidental deletion of priority matrices
        return False
admin.site.register(CandidateData)