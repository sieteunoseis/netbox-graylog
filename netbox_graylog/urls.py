"""
URL routing for NetBox Graylog Plugin.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("settings/", views.GraylogSettingsView.as_view(), name="settings"),
    path(
        "test-connection/", views.TestConnectionView.as_view(), name="test_connection"
    ),
]
