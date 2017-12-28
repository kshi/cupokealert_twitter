import twitter, re, http.client
from geopy.distance import vincenty
from discord import Webhook
import credentials

param_loc = "/home/kshi/Scripts/cupokealert/params"
discord_username = 'CU Poke Alert'
discord_avatar = 'http://i.imgur.com/75pkyxS.jpg'
Mudd = (40.809452, -73.959500)

def dist_in_km(phi, theta):
    return round(vincenty(Mudd, (phi, theta)).kilometers, 2)

api = twitter.Api(consumer_key=credentials.consumer_key,
                  consumer_secret=credentials.consumer_secret,
                  access_token_key=credentials.access_token_key,
                  access_token_secret=credentials.access_token_secret)

alerts = {1.5: {'Unown',
                'Ampharos',
                '100%'},
          1.0: {'Dragonite',
                'Tyranitar',
                'Blissey',
                '97%'},
          0.6: {'Pupitar',
                'Chansey',
                'Snorlax',
                'Lapras'},
          0.3: {'Charizard',
                'Machamp',
                'Golem',
                'Exeggutor',
                '95%'}}

params = open(param_loc,"r")
last_query_id = params.read()
params.close()
tweets = api.GetUserTimeline(screen_name='nycpokemap',since_id=last_query_id)

for tweet in reversed(tweets):
    last_query_id = tweet.id
    params = open(param_loc,"w")
    params.write(str(last_query_id))
    params.close()
    t_json = tweet._json
    text = t_json['text']
    for threshold in alerts.keys():
        if any(keyword in text for keyword in alerts[threshold]):
            gmapurl = str(t_json['entities']['urls'][1]['expanded_url'])
            nycpokemapurl = str(t_json['entities']['urls'][0]['expanded_url'])
            components = re.split('=|,', gmapurl)
            lattitude = float(components[1])
            longitude = float(components[2])
            distance = dist_in_km(lattitude, longitude)
            if distance < threshold:
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
                break
