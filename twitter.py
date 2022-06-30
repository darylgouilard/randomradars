# Using Twitter APIs

from twython import Twython
from auth import (
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)
import RandomRadars

random_player = RandomRadars.random_player

twitter = Twython(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

message = "Today's Player of the Day is " + random_player[2] + "'s " + random_player[0] + "!"
image = open('randomradar.png', 'rb')

response = twitter.upload_media(media = image)
media_id = [response['media_id']]
twitter.update_status(status = message, media_ids = media_id)
print("Successfully tweeted radar!")