import os
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from model.model import Item

SERVICE_ACCOUNT_FILE = 'google-credentials.json'
SCOPES = [
    'https://www.googleapis.com/auth/drive', 
    'https://www.googleapis.com/auth/spreadsheets'
    ]
FEEDBACKS_FOLDER_ID = os.getenv('FEEDBACKS_FOLDER_ID')
BOT_FOLDER_ID = os.getenv('BOT_FOLDER_ID')

FEEDBACKS_SHEET_INFO = 'Общая информация'
FEEDBACKS_SHEET_FEEDBACKS = 'Отзывы'
FEEDBACKS_SHEET_QUESTIONS = 'Вопросы'
FEEDBACKS_SHEET_QUESTIONSANSWERS = 'Вопросы/Ответы'


credentials = None #Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheets_service = None #build('sheets', 'v4', credentials=credentials)
drive_service = None #build('drive', 'v3', credentials=credentials)


def create_spreadsheet(item: Item) -> str:
    file_name = f'{item.name} ({item.item_id})'

    spreadsheet_body = { 'properties': { 'title': file_name } }
    spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet_body).execute()
    spreadsheet_id = spreadsheet['spreadsheetId']

    drive_service.files().update(
        fileId=spreadsheet_id,
        addParents=FEEDBACKS_FOLDER_ID,
        removeParents='root',
        fields='id, parents'
    ).execute()

    return spreadsheet_id


def delete_spreadsheet(item: Item):
    file_name = f'{item.name} ({item.item_id})'

    query = f"name='{file_name}' and '{FEEDBACKS_FOLDER_ID}' in parents"
    results = drive_service.files().list(
        q=query,
        fields="files(id, name)"
    ).execute()
    files = results.get('files', [])

    if files:
        for file in files:
            drive_service.files().delete(fileId=files[0]['id']).execute()


def create_sheets(spreadsheet_id):
    body = { "requests": [
        {"updateSheetProperties": { "properties": { "sheetId": 0, "title": FEEDBACKS_SHEET_INFO }, "fields": "title" } },
        { "addSheet": { "properties": { "title": FEEDBACKS_SHEET_FEEDBACKS } } },
        { "addSheet": { "properties": { "title": FEEDBACKS_SHEET_QUESTIONS } } },
        { "addSheet": { "properties": { "title": FEEDBACKS_SHEET_QUESTIONSANSWERS } } },
    ] }

    sheets_service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()


def write_info(item: Item, spreadsheet_id):
    body = {'values': [
        ['Бренд', item.brand],
        ['Название', item.name]
        ]}
    write_data(body, spreadsheet_id, f'{FEEDBACKS_SHEET_INFO}!A1')


def write_feedbacks(item: Item, spreadsheet_id):
    if len(item.feedbacks) == 0:
        return

    values = [['Оценка', 'Текст отзыва']]
    feedbacks = sorted(item.feedbacks, key=lambda fb: fb.productValuation, reverse=True)
    for feedback in feedbacks:
        if feedback.productValuation < 4:
            values.append([feedback.productValuation, feedback.text or ''])
    body = {'values': values}

    write_data(body, spreadsheet_id, f'{FEEDBACKS_SHEET_FEEDBACKS}!A1')


def write_questionsanswers(item: Item, spreadsheet_id):
    if len(item.questions) == 0:
        return
    
    values = [['Вопрос', 'Ответ']]
    for question in item.questions:
        values.append([question.question, question.answer])
    body = {'values': values}

    write_data(body, spreadsheet_id, f'{FEEDBACKS_SHEET_QUESTIONSANSWERS}!A1')



def write_questions(item: Item, spreadsheet_id):
    if len(item.questions) == 0:
        return
    
    values = [['Вопрос']]
    for question in item.questions:
        values.append([question.question])
    body = {'values': values}

    write_data(body, spreadsheet_id, f'{FEEDBACKS_SHEET_QUESTIONS}!A1')


def write_data(body, spreadsheet_id, range):
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range, valueInputOption='RAW', body=body
    ).execute()


def fill_data(item: Item) -> str: 
    delete_spreadsheet(item)
    spreadsheet_id = create_spreadsheet(item)
    create_sheets(spreadsheet_id)

    write_info(item, spreadsheet_id)
    write_feedbacks(item, spreadsheet_id)
    write_questions(item, spreadsheet_id)
    write_questionsanswers(item, spreadsheet_id)
    
    return spreadsheet_id
    

def get_spreadsheet_link(spreadsheet_id) -> str:
    return f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}'


def get_folder_link(folder_id) -> str:
    return f'https://drive.google.com/drive/u/0/folders/{folder_id}'