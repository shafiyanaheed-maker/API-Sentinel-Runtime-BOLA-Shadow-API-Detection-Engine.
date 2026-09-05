from detection_engine.shadow_api.detector import (
    ShadowAPIDetector
)


def test_shadow_detection():

    documented = {
        "GET /users"
    }

    observed = {
        "GET /users",
        "GET /admin"
    }

    detector = (
        ShadowAPIDetector()
    )

    result = detector.detect(
        documented,
        observed
    )

    assert (
        "GET /admin"
        in result["shadow_apis"]
    )