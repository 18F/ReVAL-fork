"""ingest URL Configuration """

from django.urls import path, re_path, include
from rest_framework import routers
from rest_framework.authtoken import views as authtoken_views

from . import api_views, views

app_name = "data_ingest"

router = routers.DefaultRouter()
router.register(r"", api_views.UploadViewSet)

urlpatterns = [
    re_path(r"^upload/(?P<replace_upload_id>\d+)?", views.upload, name="upload"),
    re_path(
        r"^review-errors/(?P<upload_id>\d+)", views.review_errors, name="review-errors"
    ),
    re_path(
        r"^confirm-upload/(?P<upload_id>\d+)",
        views.confirm_upload,
        name="confirm-upload",
    ),
    re_path(
        r"^duplicate-upload/(?P<old_upload_id>\d+)/(?P<new_upload_id>\d+)",
        views.duplicate_upload,
        name="duplicate-upload",
    ),
    re_path(
        r"^replace-upload/(?P<old_upload_id>\d+)/(?P<new_upload_id>\d+)",
        views.replace_upload,
        name="replace-upload",
    ),
    re_path(
        r"^delete-upload/(?P<upload_id>\d+)", views.delete_upload, name="delete-upload"
    ),
    re_path(
        r"^stage-upload/(?P<upload_id>\d+)", views.stage_upload, name="stage-upload"
    ),
    re_path(
        r"^upload-detail/(?P<pk>\d+)",
        views.UploadDetail.as_view(),
        name="detail",
    ),
    re_path(
        r"^insert/(?P<upload_id>\d+)",
        views.insert,
        name="insert",
    ),
    path("api/api-token-auth", authtoken_views.obtain_auth_token),
    path("api/validate", api_views.validate, name="validate"),
    path("api/", include(router.urls)),
    path(
        "",
        views.UploadList.as_view(),
        name="index",
    ),
]
