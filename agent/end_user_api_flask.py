# end_user_api_flask.py

from flask import Flask, request, jsonify
from agent import complaints_agent

app = Flask(__name__)

@app.route("/endUserChat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "")
        if not message:
            return jsonify({"response": "Waiting from your response...."}), 400

        # Get response from the agent
        response = complaints_agent(message)
        return jsonify({"response": str(response)})

    except Exception as e:
        #return jsonify({"response": f"An error occurred: {str(e)}"}), 500
        print(f"An error occurred: {str(e)}")
        return jsonify({"response": "An Error Occured, please try to raise the complaints manually..."}), 500


if __name__ == "__main__":
    app.run(debug=True, port=8000)