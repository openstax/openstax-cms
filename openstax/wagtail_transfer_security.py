"""Request-time hardening for the wagtail-transfer export API.

wagtail-transfer's *export* endpoints (``api/pages/``, ``api/models/``,
``api/objects/``, ``api/chooser/``) are not behind Django's auth/permission
system — they are protected only by an HMAC digest of
``WAGTAILTRANSFER_SECRET_KEY``. Two gaps follow from that, and this module
closes both:

1. If an environment is ever served with the placeholder secret key, the
   digest is forgeable by anyone (the placeholder is in this public repo).
   The settings-level system check can be bypassed (it does not run on a bare
   WSGI/ASGI boot), so ``block_if_insecure_key`` re-checks on every request and
   returns 403 on deployed environments still using the placeholder.

2. ``models_for_export`` / ``objects_for_export`` will serialize *any* model
   addressable by ``app_label.model`` — including ``auth.user`` (names, emails,
   password hashes). ``restrict_exportable_models`` limits them to an explicit
   allowlist: pages, images, documents, and the snippets we actually transfer.

These wrap the package views in ``openstax/wagtail_transfer_urls.py``.
"""
import json
from functools import wraps

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404

# Models always allowed through the object/model export endpoints, on top of
# whatever snippets are configured for transfer via WAGTAILTRANSFER_LOOKUP_FIELDS.
_ALWAYS_EXPORTABLE = {
    'wagtailcore.page',
    'wagtailimages.image',
    'wagtaildocs.document',
    'wagtailcore.locale',
    'contenttypes.contenttype',
    'taggit.tag',
}


def _environment_requires_secure_key():
    insecure = getattr(settings, 'WAGTAILTRANSFER_INSECURE_SECRET_KEY', 'change-me-in-production')
    return (
        getattr(settings, 'ENVIRONMENT', 'local') not in ('local', 'test')
        and getattr(settings, 'WAGTAILTRANSFER_SECRET_KEY', insecure) == insecure
    )


def block_if_insecure_key(view):
    """403 the wrapped transfer endpoint on a deployed env using the placeholder key."""
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if _environment_requires_secure_key():
            raise PermissionDenied(
                "Wagtail Transfer is disabled: WAGTAILTRANSFER_SECRET_KEY is unset "
                "or still the insecure placeholder on this environment."
            )
        return view(request, *args, **kwargs)
    return wrapped


def get_exportable_model_labels():
    """Lowercased set of model labels the export API may serve."""
    labels = set(_ALWAYS_EXPORTABLE)
    labels.update(
        label.lower()
        for label in getattr(settings, 'WAGTAILTRANSFER_LOOKUP_FIELDS', {}).keys()
    )
    labels.update(
        label.lower()
        for label in getattr(settings, 'WAGTAILTRANSFER_EXPORTABLE_MODELS', [])
    )
    return labels


def _ensure_exportable(model_path):
    if model_path is None:
        return
    if model_path.lower() not in get_exportable_model_labels():
        # 404 rather than 403: don't confirm the model exists to a caller
        # probing for arbitrary tables.
        raise Http404("Model is not exportable via wagtail-transfer.")


def restrict_exportable_models(view):
    """Limit models_for_export / objects_for_export to the allowlist.

    ``models_for_export`` takes the model in the ``model_path`` URL kwarg;
    ``objects_for_export`` takes a JSON POST body keyed by model label.
    """
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        model_path = kwargs.get('model_path')
        if model_path is not None:
            _ensure_exportable(model_path)
        else:
            # objects_for_export: model labels are the keys of the JSON body.
            # request.body is cached by Django, so the view can re-read it.
            try:
                payload = json.loads(request.body.decode('utf-8'))
            except (ValueError, TypeError, UnicodeDecodeError):
                raise PermissionDenied("Malformed wagtail-transfer object request.")
            if not isinstance(payload, dict):
                raise PermissionDenied("Malformed wagtail-transfer object request.")
            for label in payload.keys():
                if not isinstance(label, str):
                    raise PermissionDenied("Malformed wagtail-transfer object request.")
                _ensure_exportable(label)
        return view(request, *args, **kwargs)
    return wrapped
