"""Models package — import all models here so SQLAlchemy discovers them."""
from app.models.user import User          # noqa: F401
from app.models.doctor import Doctor     # noqa: F401
from app.models.clinic import Clinic     # noqa: F401
from app.models.appointment import Appointment  # noqa: F401
