import sys
import spotipy
import spotipy.util as util

scope = 'user-library-read user-modify-playback-state'

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()

token = util.prompt_for_user_token(username,
                                   scope,
                                   client_id="b8a306fd829d4ea4a757cb1411baf0eb",
                                   client_secret="a00b878607994e4fbcc08cf9c053bd21",
                                   redirect_uri="http://localhost:5000/callback/spotify")

if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_saved_tracks()
    for item in results['items']:
        track = item['track']
        print(track['name'] + ' - ' + track['artists'][0]['name'])

    results = sp.search(q="polaris masochist")
    track_id = results['tracks']['items'][0]['id']
    sp.start_playback(uris=['spotify:track:' + track_id])

else:
    print("Can't get token for", username)