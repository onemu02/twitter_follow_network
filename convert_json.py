import os
import json
import pandas as pd


def convert_json():
    df = pd.read_csv("result.csv", header=0)
    nodes = list(set(df.username.tolist() + df.follower.tolist()))
    
    datas = {
        "nodes": [{"id": user} for user in nodes],
        "links": [{"source":x, "target":y} for _,x,y in df[["username", "follower"]].to_records()],
    }
    
    with open("follow_network.json", "w") as f:
        json.dump(datas, f, indent=4)

if __name__ == "__main__":
    assert os.path.isfile("result.csv"), "Not found result.csv. Run main.py"
    convert_json()