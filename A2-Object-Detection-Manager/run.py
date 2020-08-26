from src import app
from src import background_task
import src.background

from src.worker import celery_create_worker
if __name__ == "__main__":
    # app = create_app(debug=True)
    celery_create_worker()
    app.run(host='0.0.0.0', port=5000)
