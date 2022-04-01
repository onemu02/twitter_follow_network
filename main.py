import json
import argparse
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import pandas as pd
urllib3.disable_warnings(InsecureRequestWarning)

http = urllib3.PoolManager()

BEARER_TOKEN = os.environ["TWITER_BEARER_TOKEN"]

def call_api(url: str) -> dict:
    headers = {'Authorization': 'Bearer ' + BEARER_TOKEN}
    res = http.request(method='GET',
                       url=url,
                       headers=headers,)
    if res.status != 200:
        raise urllib3.exceptions.HTTPError(res.status)
    return json.loads(res.data)


def get_user_detail(ids) -> dict:
    headers = {'Authorization': 'Bearer ' + BEARER_TOKEN}
    res = http.request(method='GET',
                       url="https://api.twitter.com/2/users",
                       headers=headers,
                       fields={
                           "ids": ids,
                           "user.fields": "created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,url,username,verified,withheld"})
    if res.status != 200:
        raise urllib3.exceptions.HTTPError(res.status)
    return json.loads(res.data)


def collect_target_follow(target_user_name:str) -> dict:
    get_user_id_url = r'https://api.twitter.com/2/users/by/username/{user_name}'.format(user_name=target_user_name)
    user_id = call_api(url=get_user_id_url).get('data').get('id')
    get_user_following_url = r'https://api.twitter.com/2/users/{id}/following?max_results=1001'.format(id=user_id)
    result = call_api(url=get_user_following_url)
    return result



def extract_target_data(data:dict) -> dict:
    d = {
        "id": data["id"],
        "username": data["username"],
        "name": data["name"],
        "description": data["description"],
        "created_at": data["created_at"],
    }
    if "entities" in data.keys():
        if "url" in data["entities"].keys():
            if "display_url" in data["entities"]["url"]["urls"][0].keys():
                d["display_url"] = data["entities"]["url"]["urls"][0]["display_url"]
                d["expanded_url"] = data["entities"]["url"]["urls"][0]["expanded_url"]
    if "mentions" in data.keys():
        d["mentions"] = {",".join([tmp["username"] for tmp in data["entities"]["description"]["mentions"]])}
    return d


def get_user_dataframe(follows):
    ids = []
    datas = []
    for _, follow in enumerate(follows["data"]):
        ids.append(follow["id"])
        if _ % 99 == 0 and _ > 0:
            r = get_user_detail(",".join(ids))
            datas += [extract_target_data(tmp) for tmp in r["data"]]
            ids = []
    r = get_user_detail(",".join(ids))
    datas += [extract_target_data(tmp) for tmp in r["data"]]
    df = pd.DataFrame(datas)
    assert df.shape[0] == len(follows["data"])
    return df


def extract_users_by(df, keyword):
    return df[df.description.str.lower().str.contains(keyword)]


def collect_twitter_network(target_username, bio_keyword):
    follows = collect_target_follow(target_username)
    user_df = get_user_dataframe(follows)
    user_df["follower"] = [target_username] * user_df.shape[0]
    extracted_user_df = extract_users_by(user_df, keyword=bio_keyword)
    return user_df, extracted_user_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='search follow network using keyword in twitter')
    parser.add_argument('username', help='twitter username', type=str)
    parser.add_argument('keyword', help='keyword for search in bio', type=str)
    args = parser.parse_args()

    TARGET_USERNAME = args.username 
    KEYWORD = args.keyword
 
    udf, edf = collect_twitter_network(TARGET_USERNAME, KEYWORD)
    udf_list = [udf]
    edf_list = [edf]
    for username in edf.username.tolist():
        _udf, _edf = collect_twitter_network(username, KEYWORD)
        udf_list.append(_udf)
        edf_list.append(_edf)

    rdf = pd.concat(edf_list)
    rdf.to_csv("result.csv", index=False)