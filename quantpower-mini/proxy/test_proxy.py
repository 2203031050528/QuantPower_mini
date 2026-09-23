import requests


def test_proxy(host, port):
    proxy_url = f"http://{host}:{port}"

    proxies = {
        "http": proxy_url,
        "https": proxy_url,
    }

    response = requests.get(
        "https://checkip.amazonaws.com",
        proxies=proxies,
        timeout=10,
    )

    return response.text.strip()
