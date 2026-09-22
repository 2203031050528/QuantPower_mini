from .models import ProxyAllocation


def generate_config():

    lines = []

    lines.append(
        """
global
    log stdout format raw

defaults
    mode tcp
    timeout connect 10s
    timeout client  1m
    timeout server  1m

"""
    )

    allocations = ProxyAllocation.objects.filter(
        is_active=True
    ).select_related("eip", "user")

    for allocation in allocations:

        lines.append(
            f"""
frontend user_{allocation.user.id}
    bind *:{allocation.proxy_port}
    default_backend user_{allocation.user.id}_backend

backend user_{allocation.user.id}_backend
    mode tcp
    server dhan dhan.example.com:443
"""
        )

    return "\n".join(lines)