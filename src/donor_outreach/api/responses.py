from flask import jsonify
from pydantic import BaseModel

def list_envelope(items: list[BaseModel]):
    return jsonify(count=len(items), items=[item.model_dump(mode="json") for item in items])


def single_envelope(item: BaseModel):
    return jsonify(item.model_dump(mode="json"))


def error_response(code: str, status: int, detail: str | None = None):
    return jsonify(error=code, detail=detail), status