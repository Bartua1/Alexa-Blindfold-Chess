from flask import Flask
from flask_ask_sdk.skill_adapter import SkillAdapter
from lambda_function import sb

app = Flask(__name__)
skill_adapter = SkillAdapter(
    skill=sb.create(),
    skill_id="amzn1.ask.skill.ead66c8d-e209-4b1a-8d3b-1dc7b4580d29",
    app=app
)

@app.route('/alexa', methods=['POST'])
def alexa_skill():
    return skill_adapter.dispatch_request()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
