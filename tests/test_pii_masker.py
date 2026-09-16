from runtime.pii_masker import mask_pii, mask_text


def test_mask_email_in_text():
    result = mask_text("Contact john@example.com for support.")

    assert "[REDACTED_EMAIL]" in result
    assert "john@example.com" not in result


def test_mask_phone_in_text():
    result = mask_text("Customer phone: +91 98765 43210")

    assert "[REDACTED_PHONE]" in result
    assert "98765 43210" not in result


def test_mask_ip_address_in_text():
    result = mask_text("Request originated from 192.168.1.25")

    assert "[REDACTED_IP]" in result
    assert "192.168.1.25" not in result


def test_mask_sensitive_dictionary_fields():
    data = {
        "email": "john@example.com",
        "phone": "+91 98765 43210",
        "password": "secret123",
        "name": "John",
    }

    result = mask_pii(data)

    assert result["email"] == "[REDACTED]"
    assert result["phone"] == "[REDACTED]"
    assert result["password"] == "[REDACTED]"
    assert result["name"] == "John"


def test_mask_nested_dictionary_fields():
    data = {
        "user": {
            "email": "john@example.com",
            "profile": {
                "phone": "+91 98765 43210",
            },
        }
    }

    result = mask_pii(data)

    assert result["user"]["email"] == "[REDACTED]"
    assert result["user"]["profile"]["phone"] == "[REDACTED]"


def test_mask_pii_inside_list():
    data = [
        {"email": "first@example.com"},
        {"email": "second@example.com"},
    ]

    result = mask_pii(data)

    assert result[0]["email"] == "[REDACTED]"
    assert result[1]["email"] == "[REDACTED]"


def test_mask_pii_inside_text_field():
    data = {
        "message": "Send details to john@example.com",
    }

    result = mask_pii(data)

    assert result["message"] == "Send details to [REDACTED_EMAIL]"


def test_non_sensitive_values_are_preserved():
    data = {
        "id": 101,
        "name": "John",
        "active": True,
        "score": 95.5,
    }

    result = mask_pii(data)

    assert result == data


def test_sensitive_token_field_is_masked():
    data = {
        "access_token": "abc123-secret-token",
        "refresh_token": "refresh-secret",
    }

    result = mask_pii(data)

    assert result["access_token"] == "[REDACTED]"
    assert result["refresh_token"] == "[REDACTED]"