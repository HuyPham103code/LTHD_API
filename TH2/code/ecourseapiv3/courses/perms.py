from rest_framework import permissions

#   bổ sung để check permission
class CommentOnwer(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, comment):
        return super().has_permission(request, view) and request.user == comment.user