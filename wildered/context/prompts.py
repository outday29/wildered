import pkgutil

from langchain.prompts import PromptTemplate


def load_template(filename: str) -> PromptTemplate:
    coder_prompt_str = pkgutil.get_data(__name__, f"prompts/{filename}").decode("utf-8")
    coder_prompt = PromptTemplate.from_template(
        template=coder_prompt_str, template_format="jinja2"
    )
    return coder_prompt


CODER_PROMPT = load_template("coder.md")
TESTER_FUNCTION = load_template("write_test.md")
