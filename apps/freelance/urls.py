from django.urls import path
from .views import FreelanceProjectListView, create_freelance_order

app_name = "freelance"

urlpatterns = [
    path("", FreelanceProjectListView.as_view(), name="project_list"),
    path("order/<int:project_id>/", create_freelance_order, name="create_order"),
]
