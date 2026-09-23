from .models import ProxyAllocation


class ProxyService:

    def get_user_proxy(self, user):
        try:
            allocation = ProxyAllocation.objects.select_related(
                "eip"
            ).get(
                user=user,
                is_active=True,
            )
        except ProxyAllocation.DoesNotExist:
            raise ValueError(
                "No active proxy allocation found for user"
            )

        return {
            "host": allocation.eip.private_ip,
            "port": allocation.proxy_port,
            "public_ip": allocation.eip.public_ip,
        }
