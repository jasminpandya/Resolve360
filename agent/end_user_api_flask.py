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
        # print type of response
        # iterate through response.message['content'] and for each item print the text between <answer> and </answer> append the output to a list and create a string from that list
        response_content = response.message['content']
        answer_texts = []
        for item in response_content:
            if isinstance(item, dict) and 'text' in item:
                text = item['text']
                start_tag = "<answer>"
                end_tag = "</answer>"
                start_index = text.find(start_tag)
                end_index = text.find(end_tag)
                if start_index != -1 and end_index != -1:
                    answer_texts.append(text[start_index + len(start_tag):end_index].strip())
        response_string = " ".join(answer_texts)
        if not response_string:
            return jsonify({"response": "No valid answer found in the response."}), 400
        

        return jsonify({"response": response_string})

    except Exception as e:
        #return jsonify({"response": f"An error occurred: {str(e)}"}), 500
        print(f"An error occurred: {str(e)}")
        return jsonify({"response": "An Error Occured, please try to raise the complaints manually..."}), 500


if __name__ == "__main__":
    app.run(debug=True, port=8000)