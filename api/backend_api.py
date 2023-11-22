from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/post", methods=["POST"])
def post_call():
    data = request.get_json()

    return jsonify(data), 201

    



if __name__ == "__main__":
    app.run(debug=True, host='ec2-3-92-216-242.compute-1.amazonaws.com')