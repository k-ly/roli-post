import json
import random
import time
import requests

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

session = requests.Session()
session.cookies.update({"_RoliVerification": config.get("roli_verification")})

playerID = config.get("player_id")
cache = {}


# Arg: user: int, Returns: set of users limiteds
def inv(user: int) -> set[int]:
    while True:
        response = requests.get('https://inventory.roblox.com/v1/users/{}/assets/collectibles?limit=100'.format(user))
        if response.status_code==200:
            inventory = json.loads(response.text)['data']
            invIDs = set()
            for asset in inventory:
                if not asset['isOnHold']:
                    invIDs.add(asset['assetId'])
            return invIDs
        else: 
            print("Error fetching inventory. Retrying in 3 seconds")
            time.sleep(3)

# Arg: cache: dict of item values, Returns: None, just updates the values in the dictionary
def updateValues(itemDict: dict) -> None:
    url= 'https://www.rolimons.com/itemapi/itemdetails'
    response = requests.get(url)
    allItems = json.loads(response.text)['items']
    for id, data in allItems.items():
        itemDict[int(id)] = data[4]
    return

# Arg: itemIds: int, Returns: set of users limiteds
def post_ad(itemIDs: list[int]) -> None:
    # default is to just ask for anything
    tags = ["demand", "any", "downgrade", "upgrade"]
    # add items ids to this if want to post a specific ad 
    reqItems = []
    tagLen = 4-len(reqItems)
    req = session.post("https://api.rolimons.com/tradeads/v1/createad", json={"player_id": playerID, "offer_item_ids": itemIDs, "request_item_ids": reqItems, "request_tags": tags[0:tagLen]})
    response = req.json()
    if response.get("success", None):
        print(f"Ad posted {itemIDs} - {tags}")
        return
    print(f'Couldn\'t post ad (Reason: {response.get("message")})')

if __name__ == "__main__":
    while True:
        # update inv and values before posting ad
        items = inv(playerID)
        updateValues(cache)
        # choose minimum value for items to be chosen at random from your inventory
        minValue = 60000
        if len(items)>4:
            randItems = random.sample([item for item in items if cache[item]>minValue],4)
        else:
            randItems = list(items)
        post_ad(randItems)
        # set amount of time before posting another ad 
        interval = 25
        print(f"Waiting {interval} minutes before attempting to post another ad")
        time.sleep(interval * 60)