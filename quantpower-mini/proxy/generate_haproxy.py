from proxy.models import ProxyAllocation


def generate_config(dhan_host):

    lines = [
        """
global
    log stdout format raw

defaults
    mode tcp
    timeout connect 10s
    timeout client 5m
    timeout server 5m
"""
    ]

    allocations = (
        ProxyAllocation.objects
        .filter(is_active=True)
        .select_related("eip", "user")
        .order_by("proxy_port")
    )

    for allocation in allocations:

        user_id = allocation.user.id
        port = allocation.proxy_port
        private_ip = allocation.eip.private_ip

        lines.append(
            f"""
frontend user_{user_id}
    bind *:{port}
    default_backend user_{user_id}_backend

backend user_{user_id}_backend
    mode tcp
    source {private_ip}
    server dhan {dhan_host}:443
"""
        )

    return "\n".join(lines)