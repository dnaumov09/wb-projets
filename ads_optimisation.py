from __future__ import annotations
import os, time, math, argparse, logging, json
from typing import List, Dict
import requests
import numpy as np
from datetime import datetime, timezone


# ──────────────────────────────────────────────────────────────────────────────
# 1. Bandit: UCB1
# ──────────────────────────────────────────────────────────────────────────────
class UCB1:
    """Класс UCB1 для k arms."""
    def __init__(self, arms: List[float], alpha: float = 2.0):
        self.arms   = arms              # список возможных ставок
        self.k      = len(arms)
        self.N      = np.zeros(self.k)  # сколько раз выбрана рука
        self.Q      = np.zeros(self.k)  # средняя награда руки
        self.alpha  = alpha             # ширина доверительного интервала
        self.t      = 0                 # номер такта

    def select(self) -> int:
        """Вернуть индекс руки для следующего интервала."""
        self.t += 1
        # сначала попробовать все руки хотя бы по разу
        for i in range(self.k):
            if self.N[i] == 0:
                return i
        # UCB-значения
        ucb = self.Q + np.sqrt(self.alpha * np.log(self.t) / self.N)
        return int(np.argmax(ucb))

    def update(self, arm_idx: int, reward: float) -> None:
        """Инкрементально обновить среднее и счётчик."""
        self.N[arm_idx] += 1
        n   = self.N[arm_idx]
        old = self.Q[arm_idx]
        self.Q[arm_idx] = old + (reward - old) / n



class WBClient:
    BASE = "https://advert-api.wb.ru"   # ⚠ Проверьте актуальный endpoint

    def __init__(self, token: str, timeout: int = 10):
        self.session = requests.Session()
        self.session.headers["Authorization"] = token
        self.timeout  = timeout

    def get_stats(self, campaign_id: int) -> Dict:
        # → /adverts/<cid>/stats?interval=5m
        url = f"{self.BASE}/adverts/{campaign_id}/stats"
        params = {"interval": "300"}      # 5 минут
        r = self.session.get(url, params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def set_bid(self, campaign_id: int, bid: float) -> None:
        # POST /adverts/{cid}/bid
        url = f"{self.BASE}/adverts/{campaign_id}/bid"
        payload = {"bid": bid}
        r = self.session.post(url, json=payload, timeout=self.timeout)
        r.raise_for_status()


# ──────────────────────────────────────────────────────────────────────────────
# 3. Campaign manager
# ──────────────────────────────────────────────────────────────────────────────
class CampaignManager:
    def __init__(self, wb: WBClient, campaign_cfg: Dict[int, List[float]]):
        """
        campaign_cfg = {campaign_id: [ставка₁, ставка₂, …]}
        """
        self.wb      = wb
        self.bandits = {cid: UCB1(arms) for cid, arms in campaign_cfg.items()}

    @staticmethod
    def reward_from_stats(stats: Dict) -> float:
        """reward = прибыль = выручка − расход на рекламу."""
        revenue = stats.get("GMV", 0.0)          # сумма заказов ₽
        spend   = stats.get("ad_spend", 0.0)     # расходы ₽
        return revenue - spend

    def update_and_bid(self):
        """Один проход: получить статистику, обновить bandit, выставить ставку."""
        for cid, bandit in self.bandits.items():
            # 1) забираем статистику интервала
            try:
                stats = self.wb.get_stats(cid)
            except Exception as e:
                logging.error("Stats error cid=%s: %s", cid, e)
                continue

            # 2) обновляем bandit прошлой наградой
            if stats:            # пропустим первый прогон без данных
                reward = self.reward_from_stats(stats)
                last_arm = int(stats.get("last_arm", -1))
                if last_arm >= 0:
                    bandit.update(last_arm, reward)

            # 3) выбираем руку, отправляем новую ставку
            arm_idx   = bandit.select()
            new_bid   = bandit.arms[arm_idx]
            try:
                self.wb.set_bid(cid, new_bid)
            except Exception as e:
                logging.error("Bid error cid=%s: %s", cid, e)
                continue

            logging.info("cid=%s  arm=%d  bid=%.2f", cid, arm_idx, new_bid)



# ──────────────────────────────────────────────────────────────────────────────
# 4. Main loop
# ──────────────────────────────────────────────────────────────────────────────
def main():
    campaign_cfg = {"23376017": [250.0, 280.0, 300.0, 320.0]}

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    wb   = WBClient("eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1NzcyOTgwNCwiaWQiOiIwMTk1OTUwMy1iOThiLTdlNTYtYjRlNS1mMTY3YTlkODRjZTQiLCJpaWQiOjE1NTAxNDc0MCwib2lkIjo0MzkwNjkzLCJzIjo3OTM0LCJzaWQiOiJjZDA3OWE1NS01NmU5LTQ1NGYtYmI0MS1jZGIwMzA4OTQ5MTMiLCJ0IjpmYWxzZSwidWlkIjoxNTUwMTQ3NDB9.YFsUKXxCozKER64Zye5cy6c-PxWmpT-GpkbopxRGZhXKX2yX54Rqwn9h-RZkHvCv9OInP-3qT64GvNN3qujXFw")
    mgr  = CampaignManager(wb, campaign_cfg)

    logging.info("Start bandit loop. Campaigns=%s", list(campaign_cfg.keys()))
    while True:
        start = time.time()
        mgr.update_and_bid()
        # спим ровно interval с учётом времени обработки
        time.sleep(max(1, 300 - (time.time() - start)))