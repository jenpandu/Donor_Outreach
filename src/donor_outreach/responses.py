""" Envelopes to wrap around our normal responses and convert Tickets into JSON """
from flask import jsonify
from pydantic import BaseModel
from collections.abc import Sequence
from donor_outreach.errors import DomainError




def list_envelope(items: Sequence[BaseModel]):
    # creates a JSON object with two properties: a count of the number of items and list of the actual items
    # could instead just do jsonify([t.model_dump(mode="json") for t in tickets]) if you only want a list returned
    return jsonify(count=len(items), items=[item.model_dump(mode="json") for item in items])

def single_envelope(item: BaseModel):
    return jsonify(item.model_dump(mode="json"))


def error_response(error: DomainError):
    return jsonify(error=error.code, detail=error.detail), error.status