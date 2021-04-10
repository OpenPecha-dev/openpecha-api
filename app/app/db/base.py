# Import all the models, so that Base has them before being
# imported by alembic
from app.db.base_class import Base
from app.models.pecha import Pecha
from app.models.user import User
