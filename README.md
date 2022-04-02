# twitter_follow_network

Search twitter user using relation of follow and keyword of bio.

## Setting

```
export TWITTER_BEARER_TOKEN="your twitter bearer token"
```

## Usage

```
poetry install
poetry run python main.py --username "USERNAME" --keyword "KEYWORD" --depth 5 --save_dir "example"
```