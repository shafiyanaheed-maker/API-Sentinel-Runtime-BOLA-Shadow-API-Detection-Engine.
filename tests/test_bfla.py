from detection_engine.bfla.detector import detect_bfla


def test_authorized_admin_access():
    result = detect_bfla(
        method="GET",
        path="/admin/users",
        user_role="admin"
    )

    assert result["detected"] is False


def test_bfla_attack():
    result = detect_bfla(
        method="GET",
        path="/admin/users",
        user_role="user"
    )

    assert result["detected"] is True
    assert result["type"] == "BFLA"
    assert result["severity"] == "HIGH"


def test_authorized_user_access():
    result = detect_bfla(
        method="GET",
        path="/profile",
        user_role="user"
    )

    assert result["detected"] is False


def test_unknown_endpoint():
    result = detect_bfla(
        method="GET",
        path="/health",
        user_role="user"
    )

    assert result["detected"] is False


def test_unknown_role():
    result = detect_bfla(
        method="GET",
        path="/admin/logs",
        user_role="guest"
    )

    assert result["detected"] is True
    assert result["type"] == "BFLA"
