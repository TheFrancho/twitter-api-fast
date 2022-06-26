#python libraries
from typing import List
import json
from datetime import datetime
from uuid import UUID, uuid4

#fastapi packages
from fastapi import APIRouter, status
from fastapi import Body, Path, HTTPException

#models modules
from models.tweet import Tweet, CreateTweet, UpdateTweet

router = APIRouter(
    prefix="/tweets",
    tags=["Tweets"],
)


@router.get(
    path = "/",
    response_model = List[Tweet],
    status_code = status.HTTP_200_OK,
    summary = "Show all Tweets",
)
def home():
    '''
    Show all tweets

    Show all the tweets stored in the db

    Parameters:
        - 
    
    Returns a json list with all tweets in the app with the following keys
        - tweet_id : UUID
        - content : str,
        - created_at : datetime,
        - updated_at : datetime,
        - by : User,
    '''
    with open("db/tweets.json", "r", encoding = 'utf-8') as f:
        results = json.load(f)
        return results


@router.post(
    path = "/post",
    response_model = Tweet,
    status_code = status.HTTP_201_CREATED,
    summary = "Post a Tweet",
)
def post_tweet(
    tweet : CreateTweet = Body(
        ...,
    )
):
    '''
    Post Tweet

    Post a Tweet in the app

    Parameters:
        - Request Body Parameters:
            - tweet : CreateTweet

    Returns a json the basic tweet information
        - tweet_id : UUID
        - content : str,
        - created_at : datetime,
        - updated_at : Optional[datetime],
        - by : UUID
    '''
    with open("db/tweets.json", "r+", encoding = 'utf-8') as f, open("db/tweets_per_person.json", "r+", encoding = 'utf-8') as logic_f:
        results = json.load(f)
        tweet_dict = tweet.dict()
        tweet_dict["tweet_id"] = uuid4()
        tweet_dict["created_at"] = datetime.now()
        tweet_dict["updated_at"] = tweet_dict["created_at"]
        results.append(tweet_dict)


        logic  = json.load(logic_f)

        found = False

        for find in logic:
            print(list(find.keys())[0])
            print()
            if str(tweet_dict["by"]) == list(find.keys())[0]:
                found = True
                find[str(tweet_dict["by"])].append(tweet_dict["tweet_id"])
                break

        if not found:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Tweet author does not exist")

        f.seek(0)
        json.dump(results, f, indent=2, default=str)
        logic_f.seek(0)
        json.dump(logic, logic_f, indent=2, default=str)
        return Tweet(**tweet_dict)


@router.get(
    path = "/tweets/{tweet_id}",
    response_model = Tweet,
    status_code = status.HTTP_200_OK,
    summary = "Show a Tweet",
)
def show_tweet(
    tweet_id: UUID = Path(
        ...
        )
):
    '''
    Show single tweet

    Show a single tweet by it id

    Parameters:
        - Path parameters:
            - tweet_id : UUID
    
    Returns a json list with the tweet info in the app with the following keys
        - tweet_id : UUID
        - content : str,
        - created_at : datetime,
        - updated_at : datetime,
        - by : User,
    '''
    with open("db/tweets.json", "r", encoding = 'utf-8') as f:
        results = json.load(f)
        for find in results:
            if find["tweet_id"] == str(tweet_id):
                return find
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tweet not found")


@router.put(
    path = "/tweets/{tweet_id}",
    response_model = Tweet,
    status_code = status.HTTP_200_OK,
    summary = "Update a Tweet",
)
def update_tweet(
    tweet_id : UUID = Path(
        ...,
    ),
    tweet : UpdateTweet = Body(
        ...,
    )
):
    '''
    Updates a tweet

    Updates the content of a Tweet

    Parameters:
        - Path parameters:
            - tweet_id : UUID
        - Body:
            - tweet : UpdateTweet
    
    Returns a json list with the tweet info in the app with the following keys
        - tweet_id : UUID
        - content : str,
        - created_at : datetime,
        - updated_at : datetime,
        - by : UUID,
    '''
    with open("db/tweets.json", "r+", encoding = 'utf-8') as f:
        tweet_dict = None
        results = json.load(f)
        for find in results:
            if find["tweet_id"] == str(tweet_id):
                tweet_dict = tweet.dict()
                for keys in find.keys():
                    if keys in tweet_dict.keys():
                        find[keys] = tweet_dict[keys]
                tweet_dict["updated_at"] = datetime.now()
                tweet_dict = find.copy()
                break
        if tweet_dict:
            f.truncate(0)
            f.seek(0)
            json.dump(results, f, indent=2, default=str)
            return Tweet(**tweet_dict)
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tweet not found")


@router.delete(
    path = "/tweets/{tweet_id}",
    response_model = Tweet,
    status_code = status.HTTP_200_OK,
    summary = "Delete a Tweet",
)
def delete_tweet(
    tweet_id : UUID = Path(
        ...,
    )
):
    '''
    Delete Tweet

    Delete the selected Tweet

    Parameters:
        - Path parameters:
            - tweet_id : UUID
    
    Returns a json object with the deleted Tweet info in the app with the following keys
        - tweet_id : UUID
        - content : str,
        - created_at : datetime,
        - updated_at : Optional[datetime],
        - by : User
    '''
    with open("db/tweets.json", "r+", encoding = 'utf-8') as f:
        results = json.load(f)
        index_to_delete = None
        for en, find in enumerate(results):
            if find["tweet_id"] == str(tweet_id):
                index_to_delete = en
                to_delete = results.pop(index_to_delete)
                break
        if index_to_delete:
            f.truncate(0)
            f.seek(0)
            json.dump(results, f, indent=2, default=str)
            return to_delete
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tweet not found")
