class ShadowAPIDetector:
    """Compare observed API traffic with documented API endpoints."""

    def detect(self, documented_endpoints, observed_endpoints):
        """Return undocumented Shadow APIs and unused Zombie APIs."""
        documented = {
            str(endpoint).strip()
            for endpoint in documented_endpoints
            if str(endpoint).strip()
        }

        observed = {
            str(endpoint).strip()
            for endpoint in observed_endpoints
            if str(endpoint).strip()
        }

        shadow_apis = sorted(observed - documented)
        zombie_apis = sorted(documented - observed)
        known_apis = sorted(observed & documented)

        return {
            "shadow_apis": shadow_apis,
            "zombie_apis": zombie_apis,
            "known_apis": known_apis,
            "count_shadow": len(shadow_apis),
            "count_zombie": len(zombie_apis),
            "count_known": len(known_apis),
        }