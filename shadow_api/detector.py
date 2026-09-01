class ShadowAPIDetector:

    def detect(self,
               documented_endpoints,
               observed_endpoints):

        shadow_apis = (
            observed_endpoints
            - documented_endpoints
        )

        zombie_apis = (
            documented_endpoints
            - observed_endpoints
        )

        return {
            "shadow_apis": list(shadow_apis),
            "zombie_apis": list(zombie_apis),
            "count_shadow": len(shadow_apis),
            "count_zombie": len(zombie_apis)
        }