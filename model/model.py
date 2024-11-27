class Feedback:
    def __init__(self, id, text, productValuation, pros, cons, answer):
        self.id = id
        self.text = text
        self.productValuation = productValuation
        self.pros = pros
        self.cons = cons
        self.answer = answer

    def __str__(self):
        return f"Feedback(id={self.id}, text={self.text}, productValuation={self.productValuation}, pros={self.pros}, cons={self.cons}, answer={self.answer})"
    

class Question:
    def __init__(self, id, question, answer):
        self.id = id
        self.question = question
        self.answer = answer


class Item:
    def __init__(self, item_id, brand=None, name=None):
        self.item_id = item_id
        self.feedbacks = []
        self.questions = []
        self.brand = brand
        self.name = name


    def add_feedbacks(self, valuation=0, valuation_sum=0, valuation_distribution={}, feedback_count=0, feedbacks_with_photo=0, feedbacks_with_text=0, feedbacks_with_video=0, feedbacks=[]):
        self.valuation = valuation
        self.valuation_sum = valuation_sum
        self.valuation_distribution = valuation_distribution
        self.feedback_count = feedback_count
        self.feedbacks_with_photo = feedbacks_with_photo
        self.feedbacks_with_text = feedbacks_with_text
        self.feedbacks_with_video = feedbacks_with_video
        self.feedbacks = feedbacks

    
    def add_questions(self, questions=[]):
        self.questions = questions