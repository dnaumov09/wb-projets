from bot import bot

from services import sheets_api, wb_api


def test():
    nm = wb_api.get_item_id('https://www.wildberries.ru/catalog/59102656/detail.aspx')

    item = wb_api.load_details(nm)
    wb_api.load_feedbacks(item)
    wb_api.load_questions(item)

    sheets_api.fill_data(item)

    return
    

if __name__ == "__main__":
    # test()
    bot.run_bot()