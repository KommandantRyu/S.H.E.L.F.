from datetime import date, datetime
from decimal import Decimal

from flask.json.provider import DefaultJSONProvider


class ShelfJSONProvider(DefaultJSONProvider):
    """Serialize MySQL/PyMySQL types (Decimal, dates) for jsonify responses."""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)
