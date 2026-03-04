from locust import task, run_single_user
from locust import FastHttpUser


class kinipk_pythonanywhere_com(FastHttpUser):
    host = "https://kinipk.pythonanywhere.com"
    default_headers = {
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "kinipk.pythonanywhere.com",
        "Pragma": "no-cache",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
    }

    @task
    def t(self):
        with self.client.request(
            "GET",
            "/",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            },
            catch_response=True,
        ) as resp:
            pass
        with self.client.request(
            "GET",
            "/static/assets/arte.png",
            headers={
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                "Referer": "https://kinipk.pythonanywhere.com/",
                "Sec-Fetch-Dest": "image",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "same-origin",
            },
            catch_response=True,
        ) as resp:
            pass
        with self.rest(
            "POST",
            "/check_user",
            headers={
                "Accept": "*/*",
                "Content-Length": "23",
                "Origin": "https://kinipk.pythonanywhere.com",
                "Referer": "https://kinipk.pythonanywhere.com/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            },
            json={"username": "TestHar2"},
        ) as resp:
            pass
        with self.client.request(
            "POST",
            "/vote",
            headers={
                "Accept": "*/*",
                "Content-Length": "144",
                "Content-Type": "application/json",
                "Origin": "https://kinipk.pythonanywhere.com",
                "Referer": "https://kinipk.pythonanywhere.com/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            },
            data='["TestHar2",["IMG-20250728-WA0025.jpg","IMG-20251027-WA0018.jpg","IMG-20250628-WA0049.jpg","IMG-20250711-WA0048.jpg","IMG-20251024-WA0034.jpg"]]',
            catch_response=True,
        ) as resp:
            pass
        with self.client.request(
            "GET",
            "/",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Referer": "https://kinipk.pythonanywhere.com/",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            },
            catch_response=True,
        ) as resp:
            pass
        with self.client.request(
            "GET",
            "/count",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            },
            catch_response=True,
        ) as resp:
            pass
        with self.client.request(
            "GET",
            "/static/assets/arte.png",
            headers={
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                "Referer": "https://kinipk.pythonanywhere.com/count",
                "Sec-Fetch-Dest": "image",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "same-origin",
            },
            catch_response=True,
        ) as resp:
            pass
        with self.client.request(
            "GET",
            "/votes",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            },
            catch_response=True,
        ) as resp:
            pass
        with self.client.request(
            "GET",
            "/admin",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            },
            catch_response=True,
        ) as resp:
            pass
        with self.client.request(
            "DELETE",
            "/delete_vote",
            headers={
                "Accept": "*/*",
                "Content-Length": "3",
                "Content-Type": "application/json",
                "Origin": "https://kinipk.pythonanywhere.com",
                "Referer": "https://kinipk.pythonanywhere.com/admin",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            },
            data='"7"',
            catch_response=True,
        ) as resp:
            pass
        with self.client.request(
            "GET",
            "/admin",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Referer": "https://kinipk.pythonanywhere.com/admin",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            },
            catch_response=True,
        ) as resp:
            pass
        with self.client.request(
            "GET",
            "/static/assets/arte.png",
            headers={
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                "Referer": "https://kinipk.pythonanywhere.com/admin",
                "Sec-Fetch-Dest": "image",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "same-origin",
            },
            catch_response=True,
        ) as resp:
            pass
        with self.client.request(
            "POST",
            "/insert",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Content-Length": "15420480",
                "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary4aUjEsNRbBsrQjJo",
                "Origin": "https://kinipk.pythonanywhere.com",
                "Referer": "https://kinipk.pythonanywhere.com/admin",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            },
            catch_response=True,
        ) as resp:
            pass
        with self.client.request(
            "GET",
            "/",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Referer": "https://kinipk.pythonanywhere.com/admin",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            },
            catch_response=True,
        ) as resp:
            pass
        with self.client.request(
            "GET",
            "/admin",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            },
            catch_response=True,
        ) as resp:
            pass


if __name__ == "__main__":
    run_single_user(kinipk_pythonanywhere_com)
