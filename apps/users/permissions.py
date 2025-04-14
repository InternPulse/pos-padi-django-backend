from rest_framework.permissions import BasePermission


class IsOwnerOrSuperuser(BasePermission):
    """
    Grants access to authenticated users with 'owner' role and superusers.
    """

    message = "Only account owners can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and ((request.user.is_authenticated
            and request.user.role == "owner")
            or request.user.is_superuser)
        )


class IsAgentOrSuperuser(BasePermission):
    """
    Grants access to authenticated users with either 'agent' role or superusers.
    """

    message = "Only agents can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and ((request.user.is_authenticated
            and request.user.role == "agent")
            or request.user.is_superuser)
        )
    

class IsOwnerOrAgentOrSuperuser(BasePermission):
    """
    Grants access to authenticated users with either 'owner', 'agent' role or superusers.
    """

    message = "Only owners or agents can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and ((request.user.is_authenticated
            and request.user.role in ["owner", "agent"])
            or request.user.is_superuser)
        )

