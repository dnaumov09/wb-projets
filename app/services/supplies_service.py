import logging
from datetime import datetime
from wildberries import hidden_api
from bot import notification_service

from admin.model import Seller

# To keep track of the previous coefficients
_previous_statuses = []
def get_supplies_offices_status(seller: Seller):
    global _previous_statuses
    try:
        new_statuses = hidden_api.get_status()
    except hidden_api.HiddenAPIException as e:
        logging.error(e)
        new_statuses = []
    
    for new_supply in new_statuses:
        for new_acceptance in new_supply.get('acceptance_costs', []):
            # Get the new coefficient
            new_coefficient = new_acceptance['coefficient']
            
            # Check for previous status for the same supply
            previous_supply = next((item for item in _previous_statuses if item['supply']['preorderId'] == new_supply['supply']['preorderId']), None)
            
            if previous_supply:
                # Find the previous coefficient for this supply
                previous_acceptance = next((item for item in previous_supply.get('acceptance_costs', []) if item['date'] == new_acceptance['date']), None)
                if previous_acceptance and previous_acceptance.get('coefficient') == -1 and new_coefficient != -1:
                    notification_service.notify_new_supply_slot(
                        seller,
                        datetime.strptime(new_acceptance['date'], "%Y-%m-%dT%H:%M:%SZ"), 
                        new_supply['supply']['warehouseName'], 
                        new_supply['supply']['preorderId'], 
                        new_coefficient, 
                        new_acceptance['cost']
                    )
    
    # Update the previous statuses to the current ones for the next check
    _previous_statuses = new_statuses
    return _previous_statuses