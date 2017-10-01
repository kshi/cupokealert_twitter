import twitter, re, http.client
from geopy.distance import vincenty
from discord import Webhook
import credentials

param_loc = "/home/kshi/Scripts/cupokealert/params"
discord_username = 'CU Poke Alert'
discord_avatar = 'http://pm1.narvii.com/5806/3200d002d594db75d61003d7dc9fd3c02762bf20_128.jpg'
Mudd = (40.8072473, -73.9615573)
max_km = 1.5

def dist_in_km(phi, theta):
    return round(vincenty(Mudd, (phi, theta)).kilometers, 3)

api = twitter.Api(consumer_key=credentials.consumer_key,
                  consumer_secret=credentials.consumer_secret,
                  access_token_key=credentials.access_token_key,
                  access_token_secret=credentials.access_token_secret)

keywords = {'Dragonite',
            'Tyranitar',
            'Chansey',
            'Blissey',
            'Pupitar',
            'Unknown',
            'Lapras',
            'Ampharos',
            'Flaaffy',
            '100%'}

params = open(param_loc,"r")
last_query_id = params.read()
params.close()
tweets = api.GetUserTimeline(screen_name='nycpokemap',since_id=last_query_id)

for tweet in reversed(tweets):
    last_query_id = tweet.id
    t_json = tweet._json
    text = t_json['text']
    for keyword in keywords:
        if keyword in text:
            gmapurl = t_json['entities']['urls'][1]['expanded_url']
            components = re.split('=|,', gmapurl)
            lattitude = float(components[1])
            longitude = float(components[2])
            distance = dist_in_km(lattitude, longitude)
            if distance < max_km:
                text = re.sub('\[.+\] ', '', text)
                text_array = text.split(' ')
                pokemon = text_array[0]
                url_nycpokemap = "<" + text_array[-2] + ">"
                url_googlemap = "<" + text_array[-1] + ">"
                text = ' '.join(text_array[0:-2])
                iv_text = re.search('IV: \d+%', text)
                cp_text = re.search('CP: \d+\)', text)
                iv = "(" + iv_text.group(0) + ")" if iv_text else ''
                cp = "(" + cp_text.group(0).replace(')','') + ")" if cp_text else ''                
                data = re.search('until.+',text).group(0)
                content = pokemon + ' ' + iv + ' ' + cp + ' (' + str(distance) + ' km) ' + data + '\n' + url_nycpokemap + '  ' + url_googlemap
                webhook = Webhook(credentials.discord_webhook, content, discord_username, discord_avatar)
                webhook.format()
                webhook.post()
                break

params = open(param_loc,"w")
params.write(str(last_query_id))
params.close()
