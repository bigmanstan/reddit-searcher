import requests
import json
import sys
import re


class Reddit:
    def __init__(self):
        self._apiurl = "https://api.reddit.com"
        self._headers = {"User-Agent": "python./all-searcher:v1.(by /u/zhiwenh)"}
        self._jsondump = False

    # searches a certain page count of /r/subreddit for certain keywords
    def all_search(self, search, subreddit="all", pages=1):
        i = 0
        after = []
        # each iteration creates JSON data of one page of Reddit material
        while i < pages:
            if i == 0:
                print("### Reddit Page 1 ###")
                print()
                response = requests.get((self._apiurl + "/r/" +subreddit), headers=self._headers)
                data = response.json()
                after.append(data["data"]["after"])  # use the after key in the JSON date and add it to the next url
                if response.status_code != 200:
                    print("Response status code: {}".format(response.status_code))
                    sys.exit()
            else:
                print()
                print("### Reddit Page {} ###".format(i+1))
                print()
                # i*25 is to simulate real reddit url count
                response = requests.get((self._apiurl + "/r/" + subreddit
                                         + "/?count=" + str(i*25) + "&after=" + after[i-1]), headers=self._headers)
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
                        print('Found a match in "{}" w/ keyword "{}"'.format(group, search[group]))
                        link = "http://www.reddit.com" + children[j]["data"]["permalink"]
                        print("Link: {}".format(link))
                        print()

            # dumps the page JSON data into jsondumpx.txt if True
            if self._jsondump is True:
                with open("jsondump" + str(i+1) + ".txt", "w") as f:
                    print("Dumping JSON data. Page {}".format(i+1))
                    json.dump(data, f, indent=4)
            i += 1

def main():
    reddit = Reddit()

    # Can search from {"title", "author", "subreddit", "url", "domain" "permalink"}
    search = {"title": input("Search reddit :")}# only strings

    search_through={"title", "author", "subreddit", "url", "domain" "permalink"}

    # Pages to search through
    pages = 5

    # Subreddit to search through
    subreddit = input("\nEnter the subreddit: ")

    reddit.all_search(search=search, subreddit=subreddit, pages=pages)

if __name__ == "__main__":
    main()
