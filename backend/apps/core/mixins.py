class OrgScopedQuerySetMixin:
    """
    Enforces automatic tenant isolation across views (Phase 0 Review Fix 5).
    Ensures querysets are strictly filtered by the authenticated user's organization.
    """

    org_field = "org"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = getattr(self.request, "user", None)

        if not user or not user.is_authenticated:
            return queryset.none()

        # In Phase 1+, User connects to Organization.
        user_org = getattr(user, "organization", None)
        if user_org is None:
            # If user has no active organization, return empty queryset to prevent leaks
            return queryset.none()

        lookup = {self.org_field: user_org}
        return queryset.filter(**lookup)
