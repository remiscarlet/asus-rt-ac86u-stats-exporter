#!/usr/bin/env python3
import requests
import base64


class AsusRouterMetricGrabber:
    LOGIN_CREDS_PATH = "secrets/login_credentials"

    LOGIN_URI = "http://router.asus.com/login.cgi"
    UPDATE_URI = "http://router.asus.com/update.cgi"
    ASUS_TOKEN = None

    def __generateLoginAuthString(self) -> str:
        with open(self.LOGIN_CREDS_PATH, "rt") as f:
            return base64.urlsafe_b64encode(f.read().encode("ascii").strip())

    def __getNewSessionToken(self) -> str:
        headers = {
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "Origin": "http://router.asus.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": "http://router.asus.com/Main_Login.asp",
        }
        data = f"group_id=&action_mode=&action_script=&action_wait=5&current_page=Main_Login.asp&next_page=index.asp&login_authorization={requests.utils.quote(self.__generateLoginAuthString())}&login_captcha="
        resp = requests.post(self.LOGIN_URI, data=data, headers=headers)
        if "asus_token" not in resp.cookies:
            raise Exception(
                "The provided authentication credentials did not work! Please check the credentials file again."
            )
        return resp.cookies["asus_token"]

    def __getToken(self) -> str:
        if self.ASUS_TOKEN is None:
            self.ASUS_TOKEN = self.__getNewSessionToken()

        # TODO: Validate token still works and recreate if it fails
        return self.ASUS_TOKEN

    def __getRawUpdateData(self):
        asus_token = self.__getToken()

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36",
            "Referer": "http://router.asus.com/Main_TrafficMonitor_realtime.asp",
            "Cookie": f"asus_token={asus_token};",
        }
        data = "output=netdev"

        resp = requests.post(self.UPDATE_URI, data=data, headers=headers)
        print(resp.text)

    def getUpdateData(self):
        self.__getRawUpdateData()


AsusRouterMetricGrabber().getUpdateData()
