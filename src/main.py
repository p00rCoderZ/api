from sanic import Sanic
from sanic.response import json
import jwt

app = Sanic()

@app.route("/", methods=['POST'])
async def test(request):
    print(request.body)
    try:
        d = jwt.decode(request.body, 'serial', algorithm='HS256')
        return json({"status": 200, "msg": "Success"})
    except jwt.exceptions.InvalidSignatureError:
        return json({"status": 400, "msg": "User not authenticated"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)