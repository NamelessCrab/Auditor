import requests, argparse

# data
accept = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
accept_lang = "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
cookie = "PHPSESSID=db8663f15799aff71beafa83f04498be; YII_CSRF_TOKEN=dc3526a3eb06cb294e684cf01486f40f287f7d0cs%3A88%3A%22U2pyTno2dTVuQ2toaUFURVAya0pWbXBlZ1huSFFuZDGD9j_-9h_VKaocGVfdIByZcJO0bvYNAE2NzhmxwxMrrQ%3D%3D%22%3B; _ym_uid=1781057732157335757; _ym_d=1781057732; _ym_isad=1; thr_view_type=83f888e2ee99c9286bdf26c0de2fa1d1ee94bcafs%3A4%3A%22list%22%3B; vul_view_type=83f888e2ee99c9286bdf26c0de2fa1d1ee94bcafs%3A4%3A%22list%22%3B"
useragent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:151.0) Gecko/20100101 Firefox/151.0"
)
headers = {"Accept": accept, "User-Agent": useragent}
url_bdu = "https://bdu.fstec.ru"
try:
    request = requests.get(url_bdu, headers, verify="./keys/")
    source = request.text
    print(source)
except requests.exceptions.SSLError:
    print("Упал на сертификате :(")
