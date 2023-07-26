class OwnedObjectsMixin:
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return super().get_queryset()
        else:
            return super().get_queryset().filter(user_id=user.id)
