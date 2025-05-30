from flask import Blueprint, request, jsonify
from openai import OpenAI
import json

trans_bp = Blueprint("trans", __name__)

client = OpenAI(api_key="<your-api-key>")  # 這裡替換成 OpenAI API 金鑰


def translate_helper(source_lang, target_lang, text):
    # translate, identify proper nouns, and explain
    response = client.responses.create(
        model="gpt-4.1",
        input=f"""
    Please translate the following {source_lang} sentence into {target_lang}. Also, identify any proper noun (such as cities, regional names, organization names, or cultural customs, but do not include country names) in the translated sentence, and give them brief explanations within 100 words. 
    Return the result in valid json format with this structure:
    {{
        "translation": "<translated text>",
        "specialized_terms": [
            {{"<specialized term>": "<explanation>"}}
        ]  # separated with comma if there are many, or return \"none\" if there is no proper noun found.
    }}
    Sentence: {text}
    """,
    )

    try:
        output = json.loads(response.output_text)
        return {"status": "success", "message": "Translation successful", **output}
    except json.JSONDecodeError as e:
        return {"status": "failure", "message": f"Failed to parse JSON: {str(e)}"}


@trans_bp.route("/", methods=["POST"])
# @jwt_required()
def translate():
    # fetch data
    post_data = request.get_json()
    source_lang = post_data.get("source_lang")
    target_lang = post_data.get("target_lang")
    text = post_data.get("text")

    result = translate_helper(source_lang, target_lang, text)
    status_code = 200 if result["status"] == "success" else 400
    return jsonify(result), status_code
