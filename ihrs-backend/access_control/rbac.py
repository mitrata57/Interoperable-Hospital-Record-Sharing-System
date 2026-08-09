from functools import wraps
from rest_framework.response import Response
from rest_framework import status


# Role → allowed actions mapping.
# kept in a central dict so that everytime a new role is created can be edited here
# no need to keep on searching in views
ROLE_PERMISSIONS = {
    "doctor": {"create_record", "view_record", "search_patient","add_lab_report"},
    "nurse": {"view_record", "add_lab_report"},
    "patient": {"view_own_record", "manage_consent"},
    "hospital_admin": {"manage_doctors", "verify_audit"},
    "receptionist": {"register_patient"},
}


def has_permission(user, action: str) -> bool:
    if not user or not user.is_authenticated:
        return False

    allowed_actions = ROLE_PERMISSIONS.get(user.role, set())
    return action in allowed_actions


def require_permission(action: str):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # A staff account with a temporary password must change
            # it before doing anything else this is enforced here,
            # BEFORE the permission check, so it applies uniformly
            # to every protected action (not just some of them).
            if request.user.must_change_password:
                return Response(
                    {"status": "error", "code": "PASSWORD_CHANGE_REQUIRED",
                     "message": "You must change your temporary password brfore proceeding."},
                    status=status.HTTP_403_FORBIDDEN
                )

            if not has_permission(request.user, action):
                return Response(
                    {"status": "error", "code": "FORBIDDEN",
                     "message": f"Your role ({request.user.role}) cannot do this action."
                               },
                    status=status.HTTP_403_FORBIDDEN
                )
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator