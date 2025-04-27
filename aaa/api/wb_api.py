import re
import requests
from aaa.model.model import Item, Feedback, Question


MAX_QUESTIONS_LOAD = 500


def get_item_id(url: str) -> str:
    try:
        return re.search(r'/catalog/(\d+)/', url).group(1)
    except:
        return None


def load_details(nm) -> Item:
    detail = requests.get(f'https://card.wb.ru/cards/v2/detail?dest=0&nm={nm}')
    product = detail.json()['data']['products'][0]
        
    return Item(product['root'], product['brand'], product['name'])


def load_questions(item: Item) -> Item:
    take, skip, count = 30, 0, None

    questions_data = []
    while (not count or skip < count and skip < MAX_QUESTIONS_LOAD): 
        response = requests.get(f'https://questions.wildberries.ru/api/v1/questions?imtId={item.item_id}&take={take}&skip={skip}')
        data = response.json()
        count = data['count']
        questions_data.extend(data['questions'])
        skip += take

    questions = []
    for question in questions_data:
        questions.append(Question(question['id'], question['text'], question['answer']['text'] if question['answer'] is not None and question['answer']['text'] is not None else None))
    
    item.add_questions(questions)


def load_feedbacks(item: Item) -> Item:
    response = requests.get(f"https://feedbacks2.wb.ru/feedbacks/v2/{item.item_id}")
    data = response.json()

    if data['feedbacks'] is None:
        response = requests.get(f"https://feedbacks1.wb.ru/feedbacks/v2/{item.item_id}")
        data = response.json()

    feedbacks = []
    for feedback in data['feedbacks']:
        feedbacks.append(Feedback(
            feedback['id'], 
            feedback['text'], 
            feedback['productValuation'], 
            feedback['pros'], 
            feedback['cons'], 
            feedback['answer'])
        )

    item.add_feedbacks(
        data['valuation'],
        data['valuationSum'],
        data['valuationDistribution'],
        data['feedbackCount'],
        data['feedbackCountWithPhoto'],
        data['feedbackCountWithText'],
        data['feedbackCountWithVideo'],
        feedbacks=feedbacks)

    return item