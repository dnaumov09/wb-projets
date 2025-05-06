import requests
from typing import List, Dict, Any

BASE_API = f"http://176.53.163.92:3000/api"
SESSION_ENDPOINT = f"{BASE_API}/session"
USER_ENDPOINT = f"{BASE_API}/user"
CARD_ENDPOINT = f"{BASE_API}/card"
# DASHBOARD_ENDPOINT = 

ADMIN_USERNAME = "dnaumov09@gmail.com"
ADMIN_PASSWORD = "newPass5"
ADMIN_USER_ID = 1

def get_session_id(username: str, password: str):
    payload = {
        "username": username,
        "password": password
    }
    response = requests.post(SESSION_ENDPOINT, json=payload)
    response.raise_for_status()
    return response.json()


SESSION_ID = get_session_id(ADMIN_USERNAME, ADMIN_PASSWORD)
HEADERS = { "X-Metabase-Session": SESSION_ID['id'] }


def _request(method: str, url: str, **kwargs) -> Any:
    """Helper to standardize API requests and error handling."""
    response = requests.request(method, url, headers=HEADERS, **kwargs)
    response.raise_for_status()
    return response.json()


def get_users():
    return _request("GET", USER_ENDPOINT)


def create_user(
    first_name: str = "Dima 2",
    last_name: str = "Naumov 2",
    email: str = "dn@dn.dn",
    password: str = "newPass5",
    group_ids: List[int] = [1]
):
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "group_ids": group_ids
    }
    return _request("POST", USER_ENDPOINT, json=payload)


def delete_user(user_id: int) -> Dict[str, Any]:
    return _request("DELETE", f"{USER_ENDPOINT}/{user_id}")


def get_cards(creator_id: int = ADMIN_USER_ID) -> List[Dict[str, Any]]:
    cards = _request("GET", CARD_ENDPOINT)
    return [card for card in cards if card.get("creator", {}).get("id") == creator_id]


def clone_card(card):
    payload = {
        "name": f"{card['name']} (Copy)",
        "description": card.get("description", ""),
        "display": card["display"],
        "collection_id": card.get("collection_id"),
        "dataset_query": card["dataset_query"]
    }
    return _request('POST', CARD_ENDPOINT, json=payload)


def clone_dashboard(dash):
    payload = {
        "name": f"{dash['name']} (Copy)",
        "description": dash.get("description", "")
    }
    res = requests.post(f"{BASE_API}/api/dashboard", json=payload, headers=headers)
    res.raise_for_status()
    new_dash = res.json()
    # Copy cards into dashboard
    cards_res = requests.get(f"{BASE_API}/api/dashboard/{dash['id']}/cards", headers=headers)
    for card in cards_res.json():
        card_config = {
            "cardId": card["card"]["id"],
            "sizeX": card["sizeX"],
            "sizeY": card["sizeY"],
            "col": card["col"],
            "row": card["row"]
        }
        add_res = requests.post(
            f"{BASE_API}/api/dashboard/{new_dash['id']}/cards",
            json=card_config, headers=headers
        )
        add_res.raise_for_status()
    print(f"✅ Cloned dashboard: {dash['name']}")
    return new_dash


def copy_dashdoards():
    new_user_id = 3
    cards = get_cards()
    print(cards)


# def get_databases():
#     url = f"{METABASE_URL}/api/database"
#     result = requests.get(url, headers=HEADERS)
#     result.raise_for_status()
#     databases = result.json()

#     print("--- 📋 Список баз данных: ---")
#     for db in databases['data']:
#         print(f"{db['id']} — {db['name']} (engine: {db['engine']})")
#     print("\n")
    
#     return databases


# def get_dashboards():
#     url = f"{METABASE_URL}/api/dashboard"
#     result = requests.get(url, headers=HEADERS)
#     result.raise_for_status()
#     dashboards = result.json()

#     print("--- 📊 Список дашбордов: ---")
#     for dashboard in dashboards:
#         print(f"{dashboard['id']} — {dashboard['name']}")

#     print("\n")
#     return dashboards


# def get_all():
#     get_databases()
#     get_dashboards()
