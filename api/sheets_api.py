import os
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

from db.models.seller import Seller
from db.models.warehouse_remains import WarehouseRemains
from db.models.remains import Remains
from db.models.card import Card

SHEETS_ADMINS = ['dnaumov09@gmail.com']

SERVICE_ACCOUNT_FILE = 'google-credentials.json'
WB_FOLDER_ID = os.getenv('WB_FOLDER_ID')

STAT_SPREADSHEET_NAME = 'Статистика'
STAT_DAILY_PIPELINE_SHEET_NAME = 'Воронка (Дни)'
STAT_DAILY_ORDERS_SHEET_NAME = 'Заказы (Дни)'
STAT_WEEKLY_ORDERS_SHEET_NAME = 'Заказы (Недели)'
STAT_MONTHLY_ORDERS_SHEET_NAME = 'Заказы (Месяца)'
STAT_DAILY_SALES_SHEET_NAME = 'Продажи (Дни)'
STAT_WEEKLY_SALES_SHEET_NAME = 'Продажи (Недели)'
STAT_MONTHLY_SALES_SHEET_NAME = 'Заказы (Месяца)'

REMAINS_SPREADSHEET_NAME = 'Склады'
REMAINS_AGGREGATED_REMAINS_SHEET_NAME = 'Остатки (общаяя статистика)'
REMAINS_REMAINS_ON_WH_SHEET_NAME = 'Остатки (по складам)'

STAT_DAILY_PIPELINE_HEADER = [
    'Дата',
    'Количество переходов в карточку товара',
    'Положили в корзину, шт.',
    'Заказали товаров, шт.',
    'Заказали на сумму, руб.',
    'Выкупили товаров, шт.',
    'Выкупили на сумму, руб.',
    'Отказов, шт.',
    'Отказов на сумму, руб.',
]

REMAINS_AGGREGATED_REMAINS_HEADER = [
    'Артикул WB',
    'Название предмета',
    'Наименование товара',
    'Артикул продавца',
    'Баркод',
    'Размер',
    'Объем, л.',
    'В пути к клиенту',
    'В пути от клиента',
    'Итоговые остатки по всем складам'
]

REMAINS_REMAINS_ON_WH_HEADER = [
    'Артикул WB',
    'Название предмета',
    'Наименование товара',
    'Артикул продавца',
    'Баркод',
    'Размер',
    'Объем, л.',
    'Название склада',
    'Количество'
]

SCOPES = [
    'https://www.googleapis.com/auth/drive', 
    'https://www.googleapis.com/auth/spreadsheets'
    ]

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)
sheets_service = build('sheets', 'v4', credentials=credentials)


def create_seller_folder(trade_mark: str, seller: Seller) -> str:
    folder_id = seller.google_drive_folder_id
    stat_spreadsheet_id = seller.google_drive_stat_spreadsheet_id
    remains_spreadsheet_id = seller.google_drive_remains_spreadsheet_id

    if folder_id is None:
        stat_spreadsheet_id = None
        remains_spreadsheet_id = None
        folder_id = create_folder(f"{trade_mark} ({seller.id})", [WB_FOLDER_ID])
    
    if stat_spreadsheet_id is None:
        stat_spreadsheet_id = create_stat_spreadsheet(folder_id)
        protect_sheets(stat_spreadsheet_id)

    if remains_spreadsheet_id is None:
        remains_spreadsheet_id = create_remains_spreadsheet(folder_id)
        protect_sheets(remains_spreadsheet_id)
    
    return folder_id, stat_spreadsheet_id, remains_spreadsheet_id


def create_folder(title, parents) -> str:
    folder_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': parents
    }
    folder = drive_service.files().create(body=folder_metadata, fields="id").execute()
    return folder.get('id')


def create_spreadsheet(title) -> str:
    spreadsheet_body = { 'properties': { 'title': title } }
    spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet_body).execute()
    return spreadsheet


def protect_sheets(spreadsheet_id):
    spreadsheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = spreadsheet_metadata.get("sheets", [])

    protect_requests = []
    for sheet in sheets:
        protect_requests.append({
            "addProtectedRange": {
                "protectedRange": {
                    "range": {
                        "sheetId": sheet["properties"]["sheetId"],
                        "startRowIndex": 0,
                        "startColumnIndex": 0
                    },
                    "warningOnly": False,
                    "editors": {
                        "users": SHEETS_ADMINS  # Only the owner can edit
                    }
                }
            }
        })

    sheets_service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": protect_requests}).execute()



def write_data(body, spreadsheet_id, range):
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range, valueInputOption='RAW', body=body
    ).execute()


def write_updated_time(spreadsheet_id, sheet_name, cell):
    body = { 
        'values': [['Updated', datetime.now().strftime("%d.%m.%Y %H:%M:%S")]] 
    }
    write_data(body, spreadsheet_id, f'{sheet_name}!{cell}')


def create_stat_spreadsheet(folder_id):
    stat_spreadsheet = create_spreadsheet(STAT_SPREADSHEET_NAME)
    stat_spreadsheet_id = stat_spreadsheet['spreadsheetId']

    drive_service.files().update(
        fileId=stat_spreadsheet_id,
        addParents=folder_id,
        removeParents='root',
        fields='id, parents'
    ).execute()

    body = { "requests": [
        {"updateSheetProperties": { "properties": { "sheetId": 0, "title": STAT_DAILY_PIPELINE_SHEET_NAME }, "fields": "title" } },
        { "addSheet": { "properties": { "title": STAT_DAILY_ORDERS_SHEET_NAME } } },
        { "addSheet": { "properties": { "title": STAT_DAILY_SALES_SHEET_NAME } } },
    ] }
    sheets_service.spreadsheets().batchUpdate(spreadsheetId=stat_spreadsheet_id, body=body).execute()

    return stat_spreadsheet_id


def update_stat_cards_sheets(stat_spreadsheet_id: str, cards: list[Card]):
    spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=stat_spreadsheet_id).execute()
    existing_sheets = spreadsheet.get('sheets', [])
    
    card_names = [c.vendor_code for c in cards]
    existing_sheets_dict = {sheet['properties']['title']: sheet['properties']['sheetId'] for sheet in existing_sheets}

    batch_update_requests = []
    clear_requests = []

    # Clear sheets that exist in both spreadsheet and names list
    for sheet_name in card_names:
        if sheet_name in existing_sheets_dict:
            clear_requests.append({
                "range": f"'{sheet_name}'"
            })

    # Add sheets that are in names list but NOT in spreadsheet
    for sheet_name in card_names:
        if sheet_name not in existing_sheets_dict:
            batch_update_requests.append({
                'addSheet': {
                    'properties': {
                        'title': sheet_name
                    }
                }
            })

    # --- Execute clear requests if any ---
    if clear_requests:
        sheets_service.spreadsheets().values().batchClear(
            spreadsheetId=stat_spreadsheet_id,
            body={'ranges': [req['range'] for req in clear_requests]}
        ).execute()

    # --- Execute batch update (delete/add sheets) if any ---
    if batch_update_requests:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=stat_spreadsheet_id,
            body={'requests': batch_update_requests}
        ).execute()



def create_remains_spreadsheet(folder_id):
    remains_spreadsheet = create_spreadsheet(REMAINS_SPREADSHEET_NAME)
    remains_spreadsheet_id = remains_spreadsheet['spreadsheetId']

    drive_service.files().update(
        fileId=remains_spreadsheet_id,
        addParents=folder_id,
        removeParents='root',
        fields='id, parents'
    ).execute()

    body = { "requests": [
        {"updateSheetProperties": { "properties": { "sheetId": 0, "title": REMAINS_AGGREGATED_REMAINS_SHEET_NAME }, "fields": "title" } },
        { "addSheet": { "properties": { "title": REMAINS_REMAINS_ON_WH_SHEET_NAME } } },
        # { "addSheet": { "properties": { "title": REMAINS_SHEET_SALES_FROM_WH } } },
    ] }
    sheets_service.spreadsheets().batchUpdate(spreadsheetId=remains_spreadsheet_id, body=body).execute()

    return remains_spreadsheet_id


def update_remains_aggregated(seller: Seller, remains: list[Remains]):
    sheets_service.spreadsheets().values().clear(spreadsheetId=seller.google_drive_remains_spreadsheet_id, range=REMAINS_AGGREGATED_REMAINS_SHEET_NAME).execute()

    values = [REMAINS_AGGREGATED_REMAINS_HEADER]
    for item in remains:
        values.append([
            item.nm_id,
            item.subject_name,
            item.card.title,
            item.vendor_code,
            item.barcode,
            item.volume,
            item.tech_size,
            item.in_way_to_client,
            item.in_way_from_client,
            item.quantity_warehouses_full
        ])

    body = { 
        'values': values 
    }
    write_data(body, seller.google_drive_remains_spreadsheet_id, f'{REMAINS_AGGREGATED_REMAINS_SHEET_NAME}!A3')
    write_updated_time(seller.google_drive_remains_spreadsheet_id, REMAINS_AGGREGATED_REMAINS_SHEET_NAME, 'A1')


def update_remains_warehouses(seller: Seller, warehouse_remains: list[WarehouseRemains]):
    sheets_service.spreadsheets().values().clear(spreadsheetId=seller.google_drive_remains_spreadsheet_id, range=REMAINS_REMAINS_ON_WH_SHEET_NAME).execute()
    
    values = [REMAINS_REMAINS_ON_WH_HEADER]
    for item in warehouse_remains:
        values.append([
            item.remains.nm_id,
            item.remains.subject_name,
            item.remains.card.title,
            item.remains.vendor_code,
            item.remains.barcode,
            item.remains.tech_size,
            item.remains.volume,
            item.warehouse.name,
            item.quantity
        ])


    body = { 
        'values': values 
    }
    write_data(body, seller.google_drive_remains_spreadsheet_id, f'{REMAINS_REMAINS_ON_WH_SHEET_NAME}!A3')
    write_updated_time(seller.google_drive_remains_spreadsheet_id, REMAINS_REMAINS_ON_WH_SHEET_NAME, 'A1')


def update_pipeline(seller: Seller, pipeline: list):
    sheets_service.spreadsheets().values().clear(spreadsheetId=seller.google_drive_stat_spreadsheet_id, range=STAT_DAILY_PIPELINE_SHEET_NAME).execute()

    values = [STAT_DAILY_PIPELINE_HEADER]
    for item in pipeline:
        values.append([
            item.get('period').strftime("%d.%m.%Y"),
            item.get('open_card_count'),
            item.get('add_to_cart_count'),
            item.get('orders_count'),
            item.get('orders_sum'),
            item.get('sales_count'),
            item.get('sales_sum'),
            item.get('orders_cancelled_count'),
            item.get('orders_cancelled_sum')
        ])
    
    body = { 
        'values': values 
    }
    write_data(body, seller.google_drive_stat_spreadsheet_id, f'{STAT_DAILY_PIPELINE_SHEET_NAME}!A3')
    write_updated_time(seller.google_drive_stat_spreadsheet_id, STAT_DAILY_PIPELINE_SHEET_NAME, 'A1')


def update_card_pipeline(seller: Seller, pipeline: list, card: Card):
    # sheets_service.spreadsheets().values().clear(spreadsheetId=seller.google_drive_stat_spreadsheet_id, range=card.vendor_code).execute()

    values = [STAT_DAILY_PIPELINE_HEADER]
    for item in pipeline:
        values.append([
            item.get('period').strftime("%d.%m.%Y"),
            item.get('open_card_count'),
            item.get('add_to_cart_count'),
            item.get('orders_count'),
            item.get('orders_sum'),
            item.get('sales_count'),
            item.get('sales_sum'),
            item.get('orders_cancelled_count'),
            item.get('orders_cancelled_sum')
        ])
    
    body = { 
        'values': values 
    }

    write_data(body, seller.google_drive_stat_spreadsheet_id, f'{card.vendor_code}!A3')
    write_updated_time(seller.google_drive_stat_spreadsheet_id, card.vendor_code, 'A1')
