from app.authorization import AuthorizationEnforcer, Role


def test_owner_can_access_their_own_object():
    auth = AuthorizationEnforcer()
    decision = auth.check_object_level("user_a", "1001")
    assert decision.allowed is True
    assert decision.violation_type is None


def test_blocks_access_to_object_owned_by_someone_else():
    auth = AuthorizationEnforcer()
    decision = auth.check_object_level("user_a", "1003")  # owned by user_b
    assert decision.allowed is False
    assert decision.violation_type == "BOLA"


def test_unknown_object_is_not_treated_as_a_violation():
    auth = AuthorizationEnforcer()
    decision = auth.check_object_level("user_a", "9999")
    assert decision.allowed is True
    assert decision.violation_type is None
    
def test_admin_role_permitted_on_admin_endpoint():
    auth = AuthorizationEnforcer()
    decision = auth.check_function_level(Role.ADMIN, "/api/admin/refund")
    assert decision.allowed is True

def test_regular_user_blocked_from_admin_endpoint():
    auth = AuthorizationEnforcer()
    decision = auth.check_function_level(Role.USER, "/api/admin/refund")
    assert decision.allowed is False
    assert decision.violation_type == "BFLA"


def test_unregistered_endpoint_defaults_to_deny():
    auth = AuthorizationEnforcer()
    # even an ADMIN should be blocked - the endpoint was never registered
    decision = auth.check_function_level(Role.ADMIN, "/api/totally/unknown")
    assert decision.allowed is False
    assert decision.violation_type == "BFLA"