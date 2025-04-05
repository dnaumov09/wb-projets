import re
from datetime import datetime
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session


def _get_existing_records(session: Session, model, data: list[dict], match_fields: list[str]):
    # Build a set of unique tuples for filtering
    key_tuples = set(tuple(item.get(field) for field in match_fields) for item in data)

    if not key_tuples:
        return {}

    # Build dynamic SQLAlchemy filters using OR of ANDs
    filters = [ 
        tuple(getattr(model, field) == value for field, value in zip(match_fields, key_tuple)) 
        for key_tuple in key_tuples
    ]

    stmt = select(model).where(or_(*[and_(*f) for f in filters]))
    existing_list = session.scalars(stmt).all()

    # Return a dict mapping keys -> object
    return {
        tuple(getattr(obj, field) for field in match_fields): obj
        for obj in existing_list
    }


def save_records(session: Session, model, data: list[dict], key_fields: list[str]):
    existing_records = _get_existing_records(
        session=session,
        model=model,
        data=data,
        match_fields=key_fields
    )

    new_records = []
    updated_records = []

    for item in data:
        key = tuple(item.get(field) for field in key_fields)

        if key in existing_records:
            obj = existing_records[key]
            for k, v in item.items():
                setattr(obj, k, v)
            updated_records.append(obj)
        else:
            obj = model()
            for k, v in item.items():
                setattr(obj, k, v)
            new_records.append(obj)
    
    if new_records:
        session.bulk_save_objects(new_records)

    session.commit()
    return new_records, updated_records


def camel_to_snake(name: str) -> str:
    name = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()


def convert_date(text, format) -> datetime:
    return datetime.strptime(text, format)