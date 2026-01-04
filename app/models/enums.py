from enum import Enum


class ClothingCategory(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    FOOTWEAR = "footwear"
    OUTERWEAR = "outerwear"
    ONE_PIECE = "one_piece"
    ACCESSORIES = "accessories"


class ColorFamily(str, Enum):
    BLACK = "Black"
    WHITE = "White"
    GREY = "Grey"
    BLUE = "Blue"
    BROWN = "Brown"
    GREEN = "Green"
    RED = "Red"
    BEIGE = "Beige"
    OTHER = "Other"


class Season(str, Enum):
    ALL_SEASON = "All-season"
    WARM = "Warm"
    COLD = "Cold"
    RAIN = "Rain"


class OutfitFeedback(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    SKIP = "skip"
    NONE = "none"


class OutfitStatus(str, Enum):
    PLANNED = "planned"
    WORN = "worn"


class NegativeReason(str, Enum):
    TOO_WARM_COLD = "Too warm/cold"
    DIDNT_LIKE = "Didn't like it"
    PLANS_CHANGED = "Plans changed"
