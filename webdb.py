import requests
import json
import os

# use this while on computer with bad ssl certificate also remove verify=False
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class webdb:
    def __init__(self):
        self.baseUrl = os.environ["url"]
        self.headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-token' : os.environ["talmido_token"]}



    def _getFromWeb(self):
        tokenGood = False
        while tokenGood == False:
            r = requests.post(self.url, data=json.dumps(self.payload), headers=self.headers, verify=False)
            if r.status_code != 200:
                os.environ["talmido_token"] = self._login()
            else:
                tokenGood = True
        return r.content.decode('utf-8')


    def _login(self):
        url = os.environ["url"]
        payload = {'username': os.environ["talmido_username"], 'password': os.environ["talmido_password"]}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        json_response = json.loads(r.content.decode('utf-8'))
        return json_response['token'] 


    def getAllQuestions(self):
        url = os.environ["url"]
        r = requests.post(url, headers=self.headers, verify=False)
        return json.loads(r.content.decode('utf-8'))

    def getQuestion(self, data):
        #{"category": "1", "data": {"masechet": "7", "page": "8"}}
        self.url = self.baseUrl + "/getQuestion"
        self.payload = data
        return self._getFromWeb()

    def updateAnswer(self, data):
        self.url = self.BaseUrl + "/updateAnswer"
        self.payload = data
        return self._getFromWeb()

        
    
