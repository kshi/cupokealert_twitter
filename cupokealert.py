import twitter, re, http.client
from geopy.distance import vincenty
from discord import Webhook
import credentials

param_loc = "/home/kshi/Scripts/cupokealert/params"
discord_username = 'CU Poke Alert'
discord_avatar = 'http://i.imgur.com/75pkyxS.jpg'
Mudd = (40.8072473, -73.9615573)
max_km = 1.5

def dist_in_km(phi, theta):
    return round(vincenty(Mudd, (phi, theta)).kilometers, 2)

api = twitter.Api(consumer_key=credentials.consumer_key,
                  consumer_secret=credentials.consumer_secret,
                  access_token_key=credentials.access_token_key,
                  access_token_secret=credentials.access_token_secret)

keywords = {'Dragonite',
            'Tyranitar',
            'Chansey',
            'Blissey',
            'Pupitar',
            'Dragonair',
            'Unknown',
            'Lapras',
            'Ampharos',
            'Flaaffy',
            'Snorlax',
            '100%',
            '97%'}

params = open(param_loc,"r")
last_query_id = params.read()
params.close()
tweets = api.GetUserTimeline(screen_name='nycpokemap',since_id=last_query_id)

for tweet in reversed(tweets):
    last_query_id = tweet.id
    t_json = tweet._json
    text = t_json['text']
    if any(keyword in text for keyword in keywords):
        gmapurl = str(t_json['entities']['urls'][1]['expanded_url'])
        nycpokemapurl = str(t_json['entities']['urls'][0]['expanded_url'])
        components = re.split('=|,', gmapurl)
        lattitude = float(components[1])
        longitude = float(components[2])
        distance = dist_in_km(lattitude, longitude)
        if distance < max_km:
            text = re.sub('\[.+\] ', '', text)
            text_array = text.split(' ')
            pokemon = text_array[0]
            url_nycpokemap = "<" + nycpokemapurl + ">"
            url_googlemap = "<" + gmapurl + ">"
            text = ' '.join(text_array[0:-2])
            iv_text = re.search('IV: \d+%', text)
            cp_text = re.search('CP: \d+\)', text)
            iv = "( " + iv_text.group(0) + " )" if iv_text else ''
            cp = "( " + cp_text.group(0).replace(')','') + " )" if cp_text else ''                
            data = re.search('until.+',text).group(0)
            content = pokemon + ' ' + iv + ' ' + cp  + ' ' + data + ' ( ' + str(distance) + ' km away )' + '\n' + url_nycpokemap + '\n' + url_googlemap
            webhook = Webhook(credentials.discord_webhook, content, discord_username, discord_avatar)
            webhook.format()
            webhook.post()

params = open(param_loc,"w")
params.write(str(last_query_id))
params.close()
