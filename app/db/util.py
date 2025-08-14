import re
import logging
from datetime import datetime
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, DisconnectionError
import time


def _get_existing_records_optimized(session: Session, model, data: list[dict], match_fields: list[str]):
    """
    Оптимизированная версия для получения существующих записей.
    Использует IN оператор вместо множественных OR условий.
    """
    if not data:
        return {}
    
    # Для простого случая с одним полем (например, rrd_id)
    if len(match_fields) == 1:
        field_name = match_fields[0]
        field_values = [item.get(field_name) for item in data if item.get(field_name) is not None]
        
        if not field_values:
            return {}
        
        # Разбиваем на батчи для избежания слишком больших IN запросов
        batch_size = 1000
        existing_records = {}
        
        for i in range(0, len(field_values), batch_size):
            batch_values = field_values[i:i + batch_size]
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    stmt = select(model).where(getattr(model, field_name).in_(batch_values))
                    batch_results = session.scalars(stmt).all()
                    
                    for obj in batch_results:
                        key = (getattr(obj, field_name),)
                        existing_records[key] = obj
                    
                    break  # Success, exit retry loop
                    
                except (OperationalError, DisconnectionError) as e:
                    if attempt < max_retries - 1:
                        logging.warning(f"Database connection error on batch {i//batch_size + 1}, attempt {attempt + 1}: {e}")
                        time.sleep(1)
                        session.rollback()
                    else:
                        logging.error(f"Failed to process batch {i//batch_size + 1} after {max_retries} attempts: {e}")
                        raise
        
        return existing_records
    
    # Для сложных случаев с несколькими полями используем старую логику
    return _get_existing_records(session, model, data, match_fields)


def _get_existing_records(session: Session, model, data: list[dict], match_fields: list[str]):
    # Build a set of unique tuples for filtering
    key_tuples = set(tuple(item.get(field) for field in match_fields) for item in data)

    if not key_tuples:
        return {}

    # Convert to list for easier processing
    key_tuples = list(key_tuples)
    
    # Process in batches to avoid huge SQL queries
    batch_size = 500  # PostgreSQL recommended batch size
    existing_records = {}
    
    for i in range(0, len(key_tuples), batch_size):
        batch = key_tuples[i:i + batch_size]
        
        # Retry logic for database connection issues
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Build dynamic SQLAlchemy filters using OR of ANDs for this batch
                filters = [ 
                    tuple(getattr(model, field) == value for field, value in zip(match_fields, key_tuple)) 
                    for key_tuple in batch
                ]

                stmt = select(model).where(or_(*[and_(*f) for f in filters]))
                batch_results = session.scalars(stmt).all()

                # Add batch results to existing_records
                for obj in batch_results:
                    key = tuple(getattr(obj, field) for field in match_fields)
                    existing_records[key] = obj
                
                break  # Success, exit retry loop
                
            except (OperationalError, DisconnectionError) as e:
                if attempt < max_retries - 1:
                    logging.warning(f"Database connection error on batch {i//batch_size + 1}, attempt {attempt + 1}: {e}")
                    time.sleep(1)  # Wait before retry
                    session.rollback()  # Rollback any failed transaction
                else:
                    logging.error(f"Failed to process batch {i//batch_size + 1} after {max_retries} attempts: {e}")
                    raise

    return existing_records


def save_records(session: Session, model, data: list[dict], key_fields: list[str]):
    # Используем оптимизированную версию для получения существующих записей
    existing_records = _get_existing_records_optimized(
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
    
    # Process new records in batches
    batch_size = 1000
    for i in range(0, len(new_records), batch_size):
        batch = new_records[i:i + batch_size]
        
        # Retry logic for database connection issues
        max_retries = 3
        for attempt in range(max_retries):
            try:
                session.bulk_save_objects(batch)
                session.flush()  # Flush to avoid memory issues
                break  # Success, exit retry loop
                
            except (OperationalError, DisconnectionError) as e:
                if attempt < max_retries - 1:
                    logging.warning(f"Database connection error on save batch {i//batch_size + 1}, attempt {attempt + 1}: {e}")
                    time.sleep(1)  # Wait before retry
                    session.rollback()  # Rollback any failed transaction
                else:
                    logging.error(f"Failed to save batch {i//batch_size + 1} after {max_retries} attempts: {e}")
                    raise

    session.commit()
    return new_records, updated_records


def camel_to_snake(name: str) -> str:
    name = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()


def convert_date(text, format) -> datetime:
    return datetime.strptime(text, format)