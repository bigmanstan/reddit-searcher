#! usr/bin/python3.5


import requests
import requests.auth
import json
from datetime import datetime
from datetime import timedelta
import sys
import re


class Reddit():
    def __init__(self):
        self._oauthurl = "https://oauth.reddit.com"
        self._headers = {"Authorization": "",
                         "User-Agent": ""}
        self._post_data = {"grant_type": "password",
                           "username": "",
                           "password": ""}
        self._auth = {"secret": "",
                      "code": ""}
        self.validtoken = False  # use to determine in main if the token is good
        self.validtime = 0
        self._jsondump = False

    def req_token(self):
        # https://github.com/reddit/reddit/wiki/OAuth2-Quick-Start-Example
        # request data, check for errors
        print("Requesting token from Reddit")
        client_auth = requests.auth.HTTPBasicAuth(self._auth["code"], self._auth["secret"])
        response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth,
                                 data=self._post_data, headers=self._headers)
        print(response.status_code)
        response.raise_for_status()

        tokendata = response.json()
        print("Token data: {}".format(tokendata))

        # exception will occur if request token succeeded
        while True:
            try:
                print("Got an error response while requesting token: {}".format(tokendata['error']))
            except:
                break
            sys.exit()

        # writes datetime and tokendata to tokendata.txt
        # prints the datetime.now() in a specific format to be strptime with the same format inputs
        with open("tokendata.txt", "w") as outfile:
            now = datetime.now()
            now = now.strftime("%Y,%m,%d,%H,%M,%S,%f")
            print(now, file=outfile)
            for key in tokendata:
                print(key, ":", tokendata[key], file=outfile)
        self._headers["Authorization"] = str(tokendata["token_type"] + " " + tokendata["access_token"])
        self.validtoken = True

    # checks to see if token is valid or not based on if file is there and time
    # returns True or False. Add ability to return token time left later
    def check_token(self):
        print("Checking token from Reddit")
        try:
            with open("tokendata.txt", "r") as f:
                f.close()
        except:
            print("No such file tokendata.txt")
            self.validtoken = False
            return

        # retrieve data from tokendata.txt
        with open("tokendata.txt", "r") as infile:
            tokendata = {}
            tokentime = None
            for i, line in enumerate(infile):
                if i == 0:
                    tokentime = line.strip("\n")
                    tokentime = datetime.strptime(str(tokentime), "%Y,%m,%d,%H,%M,%S,%f")
                else:
                    key, value = line.strip().split(':')
                    tokendata[key.strip()] = value.strip()

            print("Checking tokentime: ", tokentime)  # these two carry outside the with statement
            print("Checking tokendata: ", tokendata)

        # check to see if past token elapsed time
        expiretime = timedelta(seconds=(int(tokendata["expires_in"])))
        if (datetime.now() - tokentime) <= expiretime - timedelta(seconds=30):
            print("Valid token. Time remaining: {}".format(expiretime - (datetime.now() - tokentime)))
            self.validtoken = True
            self._headers["Authorization"] = (tokendata["token_type"] + " " + tokendata["access_token"])
        else:
            print("Need to request new token")
            self.validtoken = False
        print(self._headers["Authorization"])

    def request(self):
        def all_search(self, url="api/v1/me", ):
            response = requests.get((self._useurl + url), headers=self._headers)
            data = response.json()
            with open("jsondump2.txt", "w") as f:
                json.dump(data, f, indent=4)

    # searches a certain page count of /r/all for certain keywords
    def all_search(self, search, count=0):
        i = 0
        after = []
        # each iteration creates JSON data of one page of Reddit material
        while i <= count:
            if i == 0:
                print("### Reddit Page 1 ###")
                print()
                response = requests.get((self._oauthurl + "/r/all"), headers=self._headers)
                data = response.json()
                after.append(data["data"]["after"])  # use the after key in the JSON date and add it to the next url
            else:
                print()
                print("### Reddit Page {} ###".format(i + 1))
                print()
                # i*25 is to simulate real reddit url
                # need to check how viewing more than 25 pages affects this
                response = requests.get((self._oauthurl + "/r/all/?"
                                         + "count=" + str(i * 25) + "&after=" + after[i - 1]), headers=self._headers)
                data = response.json()
                after.append(data["data"]["after"])

            # iterates through each of the links on the Reddit page
            children = data["data"]["children"]
            for j, listing in enumerate(children):
                # uses a regex with the search group and its respective search keyword. Prints link if match
                for group in search:
                    # print("Searching thru {}".format(group))
                    pattern = re.compile(search[group], re.IGNORECASE)
                    value = children[j]["data"][group]
                    if re.search(pattern, value):
                        print("Found a match in {} w/ keyword {}".format(group, search[group]))
                        link = "http://www.reddit.com" + children[j]["data"]["permalink"]
                        print("Link: {}".format(link))
                        print()

            # dumps the page JSON data into jsondumpx.txt
            if self._jsondump is True:
                with open("jsondump" + str(i) + ".txt", "w") as f:
                    print("Dumping JSON data. Page {}".format(i))
                    json.dump(data, f, indent=4)
            i += 1


def main():
    reddit = Reddit()
    reddit.check_token()
    if reddit.validtoken is False:
        reddit.req_token()
    print()
    search = {"title": "donald|sanders", "subreddit": "donald|sanders"}  # only string attributes
    reddit.all_search(search=search, count=20)


if __name__ == "__main__":
    main()
