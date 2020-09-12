from flask import Flask, redirect, url_for, session
from flask_oauth import OAuth
from functools import wraps
try:
    from urllib.request import Request, urlopen
    from urllib.error import URLError
except Exception as e:
    from urllib2 import Request, urlopen, URLError
import random

# You must configure these 3 values from Google APIs console
# https://code.google.com/apis/console
GOOGLE_CLIENT_ID = 'YOUR-GOOGLE-CLIENT-ID'
GOOGLE_CLIENT_SECRET = 'YOUR-GOOGLE-SECRET'
REDIRECT_URI = '/authorized'  # one of the Redirect URIs from Google APIs console
BASE_URL = "http://localhost:5000/"


SECRET_KEY = 'development key'
DEBUG = True

app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

d = {"canned ache my high saw few": "can’t take my eyes off you", "yeah skew ween": "yes queen", 
"knew foam hood is ": "new phone,who this??", "hiss sit tinny it": "is it in yet?",
 "wind her ritz cun ink": "winter is coming", " essay madder rough act": "as a matter of fact", 
 "dawn dutch mice tough": "don’t touch my stuff", "uke ant an dell tat ruth": "you can’t handle the truth", 
 "fun elle eyes": "vanilla ice", "ford went he": "420", "hint turn ed rolls": "internet trolls",
  "sick steamy knits":"60 minutes","meow tin deh whew":"mountain dew" ,
  "dawn biafra eight duff deed arc": "don’t be afraid of the dark", "my crows off tex sell": "microsoft excel",
   "haystack up hank aches ": "a stack of pancakes", "tethers diss rall": "the thirst is real",
    "Car own hu fire us": "coronavirus", "foal hip cub": "flip cup", "sped doors wall hoe": "split or swallow", 
    "ace lip puff that hung": "a slip of the tongue", "bull lag fried hay": "black friday",
     "tock toothy and": "talk to the hand", "calm heed at tea": "call me daddy",
      "made divorce pea whiff ewe": "may the force be with you","muff heater gold ":"my feet are cold", 
      "hoop heard rife fair": "uber driver", "par dave owl": "party owl", "gnome morse ghoul": "no more school",
       "ditch chews haze hum thinn": "did you say something", 
       "sups cur ripe tomb eye sham null": "subscribe to my channel", "stir range earth inks ": "stranger things",
        "abe aura her she’s chalk lit": "a bar of hershey’s chocolate", "real agents ship gulls":"relationship goals",
        "test brit how survives":"desperate housewives","sew shall diss ten sing": "social distancing",
        "mere ores elf free":"mirror selfie","bat tree snot ink looted ": "batteries not included", 
        "nosed ring sat hatched": "no strings attached", "was estrange lank wedge": "what a strange language",
         "fin day hoe gains":"video games", "hoop side hid ditto ken": "oops I did it again", 
         "lib full half all of": "live,laugh,love", "eye yam stew peed": "I am stupid", 
         "moor nim bur wrath": "morning breath", "chest who wit": "just do it", 
            "hood pubes avery won": "good new everyone", "bone apple teeth": "bon appetit", 
            "ewe knight taking dumb": "united kingdom","hood pubes Avery won ": "good news everyone", 
            "Thirds teeth or stay": "thirsty thursday", "pie Juan kit won furry ": "buy 1 get 1 free", 
            "pull ease leaf mia alone": "please leave me alone", "yew login lie ugh snap": "you lookin' like a snack",
             "Thirst rug el isreal ": "the struggle is real", "Muh knees hot ": "money shot", 
             "hue only lee leaf one": "you only leave once", "Shelf dry fink curse": "self driving cars", 
             "weigh cup toothy fax": "wake up to the facts", "Hug cup called sure": "hookup culture", 
             "pole eddy clicker wrecked": "politically correct", "bull lag fried hay": "black friday",
             "Tech a gel pel": "take a chill pill", "pretty shack scent": "British accent", 
             "All huck each arm": "a lucky charm", "phase poke off his shoal": "Facebook official", 
             "High lie kit her of": "I like it rough", "Toy lit issue": "toilet tissue", 
             "sore hay nods ore hee": "sorry not sorry", "Sun nab shat filled her": "snapshot filter", 
             "Dez pus seed hoe": "despacito", "donut hawk twos train jazz":"donot talk to strangers", 
             "Enter net vain muss": "internet famous", "Utah kin tomb he": "you talking to me ??", 
             "Fish hits bin hers": "fidget spinners", "chest in bee bear": "Justin beiber", 
             "Igloo tin fry yee": "gluten -free", "Eye low ves alls age": "I love sausage",
              "foyer inn form hay shun": "for your information"}

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)




def check_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('access_token') is None:
            return redirect(BASE_URL + url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))

    return render_template('index.html')

    access_token = access_token[0]


    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except Exception as  e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('login'))
        return res.read()

    return render_template("login.html")


@app.route("/q")
@check_login
def ques():
    return random.choice(list(d.keys()))

@app.route("/ans")
@check_login
def ans():
    p = request.args.get('p')
    return d[p]

@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)



@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
