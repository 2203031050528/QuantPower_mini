from django.db import transaction

from .models import EIPPool, ProxyAllocation


class ProxyAllocator:

    BASE_PORT = 9000

    @transaction.atomic
    def allocate(self, user):

        existing = ProxyAllocation.objects.filter(
            user=user,
            is_active=True,
        ).first()

        if existing:
            return existing

        eip = (
            EIPPool.objects
            .select_for_update()
            .filter(is_allocated=False)
            .first()
        )

        if not eip:
            raise ValueError(
                "No EIP available"
            )

        used_ports = set(
            ProxyAllocation.objects.values_list(
                "proxy_port",
                flat=True,
            )
        )

        port = self.BASE_PORT

        while port in used_ports:
            port += 1

        allocation = ProxyAllocation.objects.create(
            user=user,
            eip=eip,
            proxy_port=port,
        )

        eip.is_allocated = True
        eip.save(
            update_fields=["is_allocated"]
        )

        return allocation