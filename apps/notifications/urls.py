from django.urls import path
from .views import mark_read, mark_all_read

app_name = "notifications"

urlpatterns = [
    path("mark-read/<int:notif_id>/", mark_read, name="mark_read"),
    path("mark-all-read/", mark_all_read, name="mark_all_read"),
]
