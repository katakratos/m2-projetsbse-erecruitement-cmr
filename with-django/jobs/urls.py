from django.urls import path
from . import views

urlpatterns = [
    path('', views.JobListView.as_view(), name='job_list'),
    path('<int:job_id>/', views.JobDetailView.as_view(), name='job_detail'),
    path('create/', views.JobCreateView.as_view(), name='job_create'),
    path('<int:job_id>/update/', views.JobUpdateView.as_view(), name='job_update'),
    path('<int:job_id>/criteria/add/', views.AddCriteriaView.as_view(), name='add_criteria'),
    path('criteria/<int:criteria_id>/delete/', views.DeleteCriteriaView.as_view(), name='delete_criteria'),  # New URL pattern
    path('<int:job_id>/ahp-matrix/', views.AHPMatrixView.as_view(), name='ahp_matrix'),
    path('<int:job_id>/ahp-suggestions/', views.AHPSuggestionsView.as_view(), name='ahp_matrix_suggestions'),
    path('test-ahp-matrix/', views.TestAHPMatrixView.as_view(), name='test_ahp_matrix'),
    path('<int:job_id>/process-applications/', views.ProcessJobApplicationsView.as_view(), name='process_applications'),
    path('<int:job_id>/candidate-results/', views.CandidateResultsView.as_view(), name='view_candidate_results'),
    path('<int:job_id>/processing-status/', views.ApplicationProcessingStatusView.as_view(), name='processing_status'),
    path('<int:job_id>/rank-candidates/', views.RankCandidatesAHPView.as_view(), name='rank_candidates'),
    path('<int:job_id>/genetic-team/', views.GeneticTeamView.as_view(), name='genetic_team'),
]
