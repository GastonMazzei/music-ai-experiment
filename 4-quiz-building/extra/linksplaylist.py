import googleapiclient.discovery
from urllib.parse import parse_qs, urlparse

def parse_playlist_please(url):
  query = parse_qs(urlparse(url).query, keep_blank_values=True)
  playlist_id = query["list"][0]
  print(f'get all playlist items links from {playlist_id}')
  youtube = googleapiclient.discovery.build("youtube", "v3", 
  developerKey = devkey_)
  request = youtube.playlistItems().list(
    part = "snippet",
    playlistId = playlist_id,
    maxResults = 200
  )
  response = request.execute()
  playlist_items = []
  while request is not None:
    response = request.execute()
    playlist_items += response["items"]
    request = youtube.playlistItems().list_next(request, response)
  print(f"total: {len(playlist_items)}")
  casos = {}
  for t in playlist_items:
    casos[t['snippet']['title'].split(' ')[-1]] = f'https://www.yout'\
  f'ube.com/watch?v={t["snippet"]["resourceId"]["videoId"]}&list={playlist_id}&t=0s'
  return casos

if __name__=='__main__':
  devkey_ = input('please enter the Google Developer Key')
  cases = parse_playlist_please(input('please enter the playlist link'))
  keylist = {}  
  with open('refs.dat','r') as f:
    for x in f:
      temp = x.split(' ')
      keylist[temp[1]] = keylist.get(temp[1],[])+[temp[0]]
  print(keylist.keys())
  with open('links.dat','w') as f:
    for x in keylist.keys():
      f.write(f'var {x} =\n[')
      for y in keylist[x]:
        try:
          f.write('"'+cases[y]+'",\n')
        except KeyError: 
          print(f'composer {x} wasnt in {y}')
      f.write(']\n\n')
  print('ENDED SUCCESSFULLY!')


