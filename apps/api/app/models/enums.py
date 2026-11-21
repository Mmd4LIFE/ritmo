import enum


class Locale(str, enum.Enum):
    EN = "en"
    FA = "fa"


class HabitKind(str, enum.Enum):
    WATER = "water"
    STUDY = "study"
    GYM = "gym"
    NO_SMOKING = "no_smoking"
    CUSTOM = "custom"


class CalendarSource(str, enum.Enum):
    MANUAL = "manual"
    BILL = "bill"
    HABIT = "habit"
    CYCLE = "cycle"
    DIGEST = "digest"


class BillRecurrence(str, enum.Enum):
    ONCE = "once"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    WEEKLY = "weekly"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PlanCode(str, enum.Enum):
    FREE = "free"
    PREMIUM = "premium"
