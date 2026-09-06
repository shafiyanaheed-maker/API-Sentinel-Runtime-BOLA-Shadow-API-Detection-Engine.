from detection_engine.bola.detector import detect_bola


def test_authorized_object_access():
    result = detect_bola(
        method="GET",
        path="/users/101",
        authenticated_user_id=101
    )

    assert result["detected"] is False


def test_authorized_multiple_objects():
    result = detect_bola(
        method="GET",
        path="/users/105",
        authenticated_user_id=101
    )

    assert result["detected"] is False


def test_bola_attack():
    result = detect_bola(
        method="GET",
        path="/users/102",
        authenticated_user_id=101
    )

    assert result["detected"] is True
    assert result["type"] == "BOLA"
    assert result["severity"] == "HIGH"


def test_unknown_resource():
    result = detect_bola(
        method="GET",
        path="/health",
        authenticated_user_id=101
    )

    assert result["detected"] is False


def test_unknown_user():
    result = detect_bola(
        method="GET",
        path="/users/101",
        authenticated_user_id=999
    )

    assert result["detected"] is True
    assert result["type"] == "BOLA"