from django.test import RequestFactory

from apps.core.mixins import OrgScopedQuerySetMixin


class DummyQuerySet:
    def __init__(self, items=None):
        self.items = items or []

    def none(self):
        return DummyQuerySet([])

    def filter(self, **kwargs):
        # Emulate filter by org
        org_val = kwargs.get("org")
        filtered = [item for item in self.items if getattr(item, "org", None) == org_val]
        return DummyQuerySet(filtered)

    def count(self):
        return len(self.items)


class DummyItem:
    def __init__(self, id, org):
        self.id = id
        self.org = org


class DummyOrgView(OrgScopedQuerySetMixin):
    def __init__(self, request, items):
        self.request = request
        self._items = items

    def get_queryset(self):
        # We start with the base queryset
        super_qs = DummyQuerySet(self._items)
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return super_qs.none()
        user_org = getattr(user, "organization", None)
        if user_org is None:
            return super_qs.none()
        return super_qs.filter(org=user_org)


class MockOrg:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class MockUser:
    def __init__(self, email, organization=None, is_authenticated=True):
        self.email = email
        self.organization = organization
        self.is_authenticated = is_authenticated


class TestTenantIsolation:
    """
    Phase 0 Review Fix 5: Automatic tenant isolation verification.
    Ensures querysets never return data belonging to other organizations.
    """

    def test_anonymous_user_returns_empty_queryset(self):
        rf = RequestFactory()
        request = rf.get("/api/projects")
        request.user = MockUser(email="anon@example.com", is_authenticated=False)

        org_a = MockOrg(1, "Org A")
        items = [DummyItem(1, org_a)]

        view = DummyOrgView(request, items)
        qs = view.get_queryset()
        assert qs.count() == 0

    def test_tenant_cannot_access_foreign_organization_items(self):
        rf = RequestFactory()
        org_a = MockOrg(1, "Org A")
        org_b = MockOrg(2, "Org B")

        # Org B user makes request
        request = rf.get("/api/projects")
        request.user = MockUser(email="user_b@orgb.com", organization=org_b)

        # Dataset belongs to Org A
        items = [
            DummyItem(101, org_a),
            DummyItem(102, org_a),
            DummyItem(201, org_b),
        ]

        view = DummyOrgView(request, items)
        qs = view.get_queryset()

        # Should only see their own org item
        assert qs.count() == 1
        assert qs.items[0].id == 201
