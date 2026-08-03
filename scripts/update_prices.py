import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.price_updater import update_prices_batch
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    count = update_prices_batch(interval_hours=interval)
    print(f"Обновлено {count} цен")