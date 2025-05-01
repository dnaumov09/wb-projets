import logging
import time
import argparse
import utils.logging_settings as logging_settings

from admin.timeweb_api import create_databases
from admin.wildberries_api import get_seller_info
from admin.db_api import init_databases


def main(token: str):
    seller_info = {
        'token': token,
        **get_seller_info(token)
    }

    databases = create_databases(seller_info)
    logging.info('--- Waiting for 5 seconds before processing with databases')
    time.sleep(5)
    init_databases(seller_info, databases)


if __name__ == "__main__":
    logging_settings.init_logging(logging_settings.logging.INFO)
    parser = argparse.ArgumentParser()
    #EMBEK
    # TOKEN = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1NzQ2Nzc4NSwiaWQiOiIwMTk1ODU2NS1hNDU5LTc0MTYtODIxNi1kOTk4NjkzMTMyNTgiLCJpaWQiOjkwNjE4MzQsIm9pZCI6Njg0ODc4LCJzIjoxMDczNzQ5NzU4LCJzaWQiOiI5OTAzNzg1MS03NjdkLTQwMWItYjNhMy1lY2VkOGRiMTJlYmUiLCJ0IjpmYWxzZSwidWlkIjo5MDYxODM0fQ.phXr9uGRYOvuWymaGp3RdkZsDjafPQtMDWPwE2syl97sVnaonuw2CDJeb2SBr2f1ZkT6UfVN24wtOND89ESd0w'
    #BS
    # TOKEN = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwNDE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MTQ0Nzg5OSwiaWQiOiIwMTk2NzJhMS01OWY5LTcyM2YtYTA5MC1mZDljYmFiMDc0ZGMiLCJpaWQiOjE1NTAxNDc0MCwib2lkIjo0MzkwNjkzLCJzIjoxMDczNzQ5NzU4LCJzaWQiOiJjZDA3OWE1NS01NmU5LTQ1NGYtYmI0MS1jZGIwMzA4OTQ5MTMiLCJ0IjpmYWxzZSwidWlkIjoxNTUwMTQ3NDB9.hkRjl-ZMIkQ_QjTbCaMdp7aPYLdGNxU4eQ0tT89Mc-mKpKorGMNExMS8mmMar_kOoUnCC0Fk_nGJ_etoFANHxA"
    TOKEN = ''
    parser.add_argument('--token', type=str, required=False, default=TOKEN)
    args = parser.parse_args()
    main(args.token)
