from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Grants access only to authenticated users with 'owner' role.
    """

    message = "Only account owners can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "owner"
        )


class IsAgent(BasePermission):
    """
    Grants access to authenticated users with either 'owner' or 'agent' role.
    Owners inherit all agent permissions.
    """

    message = "Only owners or agents can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in {"owner", "agent"}
        )
