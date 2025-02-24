from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView
from django.http import Http404
from rest_framework.exceptions import APIException
from rest_framework import status

from .api_views import UploadViewSet
from . import ingest_settings

UploadModel = ingest_settings.upload_model_class


class Api:
    @staticmethod
    def call(request, what, pk=None):
        """
        Proxy a call to the internal API.

        :param request: The current HttpRequest object.
        :param what: The viewset action to invoke on the API ("list",
          "create", "retrieve", "update", "partial_update", or "destroy")
        :param pk: the given id, not applicable if action is "list" or "create"
        :raises: Http404 if object is not found, APIException if non 2xx or 404.
        """
        method = request.method.lower()
        func = UploadViewSet.as_view({method: what})
        api_response = func(request, pk=pk)
        if status.is_success(api_response.status_code):
            return
        if api_response.status_code == 404:
            raise Http404(api_response.reason_phrase)
        # we most likely have an internal API error here.
        error = f"API returned {api_response.status_code}: {api_response.reason_phrase}"
        raise APIException(error)


class UploadList(LoginRequiredMixin, ListView):
    model = UploadModel
    template_name = ingest_settings.UPLOAD_SETTINGS["LIST_TEMPLATE"]

    def get_queryset(self):
        return (
            UploadModel.objects.filter(submitter=self.request.user)
            .exclude(status="DELETED")
            .order_by("-created_at")
        )


class UploadDetail(LoginRequiredMixin, DetailView):
    model = UploadModel
    template_name = ingest_settings.UPLOAD_SETTINGS["DETAIL_TEMPLATE"]


@login_required
def duplicate_upload(request, old_upload_id, new_upload_id):
    old_upload = UploadModel.objects.get(pk=old_upload_id)
    new_upload = UploadModel.objects.get(pk=new_upload_id)

    data = {"old_upload": old_upload, "new_upload": new_upload}

    return render(request, "data_ingest/duplicate_upload.html", data)


@login_required
def replace_upload(request, old_upload_id, new_upload_id):
    """
    Replaces an upload with another upload already in progress.
    """

    old_upload = UploadModel.objects.get(pk=old_upload_id)
    new_upload = UploadModel.objects.get(pk=new_upload_id)

    new_upload.replaces = old_upload
    new_upload.save()
    return validate(new_upload)


@login_required
def delete_upload(request, upload_id):
    Api.call(request, "destroy", pk=upload_id)
    return redirect("data_ingest:index")


def validate(instance):
    ingestor = ingest_settings.ingestor_class(instance)
    instance.validation_results = ingestor.validate()
    instance.save()
    if instance.validation_results["valid"]:
        return redirect("data_ingest:confirm-upload", instance.id)
    else:
        return redirect("data_ingest:review-errors", instance.id)


# working on this
@login_required
def upload(request, replace_upload_id=None, **kwargs):
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = ingest_settings.upload_form_class(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            metadata = dict(form.cleaned_data.items())
            metadata.pop("file")
            replace_upload_id = metadata.pop("replace_upload_id")
            instance = ingest_settings.upload_model_class(
                file=request.FILES["file"],
                submitter=request.user,
                file_metadata=metadata,
                raw=form.cleaned_data["file"].read(),
            )
            instance.save()
            if replace_upload_id is None:
                replace_upload = instance.duplicate_of()
                if replace_upload:
                    return redirect(
                        "data_ingest:duplicate-upload", replace_upload.id, instance.id
                    )
            else:
                Api.call(request, "destroy", pk=int(replace_upload_id))

            return validate(instance)

    else:
        initial = request.GET.dict()
        initial["replace_upload_id"] = replace_upload_id
        form = ingest_settings.upload_form_class(initial=initial)

    return render(request, ingest_settings.UPLOAD_SETTINGS["TEMPLATE"], {"form": form})


def review_errors(request, upload_id):
    upload = UploadModel.objects.get(pk=upload_id)
    if upload.validation_results["valid"]:
        return redirect("data_ingest:confirm-upload", upload_id)
    data = upload.validation_results["tables"][0]
    data["file_metadata"] = upload.file_metadata_as_params()
    data["upload_id"] = upload_id
    return render(request, "data_ingest/review-errors.html", data)


def confirm_upload(request, upload_id):
    upload = UploadModel.objects.get(pk=upload_id)
    data = upload.validation_results["tables"][0]
    data["file_metadata"] = upload.file_metadata_as_params()
    data["upload_id"] = upload.id
    return render(request, "data_ingest/confirm-upload.html", data)


def stage_upload(request, upload_id):
    Api.call(request, "stage", pk=upload_id)
    return redirect("data_ingest:index")


def detail(request, upload_id):
    upload = UploadModel.objects.get(pk=upload_id)
    if upload.status == "LOADING":
        if upload.validation_results["valid"]:
            return redirect("data_ingest:confirm-upload", upload_id)
        else:
            return redirect("data_ingest:review-errors", upload_id)
    else:
        return redirect("data_ingest:upload-detail", upload_id)


def insert(request, upload_id):
    try:
        Api.call(request, "insert", pk=upload_id)
        return redirect("data_ingest:index")
    except APIException:
        return redirect("data_ingest:upload-detail", upload_id)
