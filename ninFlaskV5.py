from threading import Thread
from flask import Flask, request
import json
import v5path
from EGAM import EGAM

app = Flask("app")
ipath = v5path.ipath
ipath2 = v5path.ipath2
BOTTOKEN = v5path.BOTTOKEN

CLIENT_ID = v5path.CLIENT_ID
CLIENT_SECRET = v5path.CLIENT_SECRET
REDIRECT_URI = v5path.REDIRECT_URI

egam = EGAM(bot_token=BOTTOKEN,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI)


@app.route('/', methods=["GET"])
def index():
  html = '''
  <!DOCTYPE html>
  <html lang=”ja”>
  <head>
  <meta charset=”UTF-8″>
  </head>
    <style>
      html,body {
      overflow: hidden;
      }
    </style>
  <p style="font-size: 90px;font-weight: bold;margin-top: 0.3em;margin-right: 0.5em;margin-left: 0.5em;margin-bottom: 0.5px;background-color: #51fc54;text-align: center;border-radius:20px;color: #fffcde;">認証完了</p>
  <p style="font-size: 50px;font-weight: bold;margin-top: 0.3em;margin-right: 0.5em;margin-left: 0.5em;margin-bottom: 0.5px;background-color: #399800;text-align: center;border-radius:20px;color: #ffffff;"><br>このサーバーへ<br> ようこそ！<br>待ってました！<br>　</p>
  </body>
  </html>'''
  try:
    code = request.args.get('code', '')
    if code == "":
      return
    state = request.args.get('state', '').split("-")
    serverstate = int(state[0], 16)
    rolestate = int(state[1], 8)
    try:
      serveridj = open(f"{ipath2}{serverstate}.json")
    except:
      return

    gettoken = egam.get_token(code)
    token = gettoken['access_token']
    getuser = egam.get_user(token)
    user = getuser["id"]
    name = getuser["username"]
    addrole = egam.add_role(user_id=user,
                            guild_id=str(serverstate),
                            role_id=str(rolestate))
    if not addrole == 204:
      return f"<h1>ロールの付与に失敗しました<br>Botがロールを付与できる状態か確認してください<br>Botのロールが付与したいロールの1つ上に置かれていない場合や、管理権限に2段階認証が必要になっている場合ロールが付与できません！</h1>"

    serverid = json.load(serveridj)
    useridj = open(ipath)
    userid = json.load(useridj)

    if not user in serverid.keys():
      serverid.update({user: f"{len(userid)}"})
      json.dump(serverid, open(f"{ipath2}{serverstate}.json", "w"))

    if not token in userid.values():
      userid.update({user: token})
      json.dump(userid, open(f"{ipath}", "w"))

  except Exception as e:
    return f"<span>エラー : {e}</span>"

  return html


def run():
  app.run(debug=False, host="0.0.0.0")


def start():
  t = Thread(target=run)
  t.start()
