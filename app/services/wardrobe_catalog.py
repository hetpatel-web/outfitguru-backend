from app.models.enums import ClothingCategory, ColorFamily, Season

WARDROBE_CATEGORIES = [
    {
        "slug": ClothingCategory.TOP,
        "label": "Top",
        "subtypes": ["General", "T-shirt", "Shirt", "Sweater", "Blouse"],
    },
    {
        "slug": ClothingCategory.BOTTOM,
        "label": "Bottom",
        "subtypes": ["General", "Jeans", "Trousers", "Shorts", "Skirt"],
    },
    {
        "slug": ClothingCategory.ONE_PIECE,
        "label": "One-Piece",
        "subtypes": ["General", "Dress", "Jumpsuit", "Rompers"],
    },
    {
        "slug": ClothingCategory.OUTERWEAR,
        "label": "Outerwear",
        "subtypes": ["General", "Jacket", "Coat", "Hoodie"],
    },
    {
        "slug": ClothingCategory.FOOTWEAR,
        "label": "Footwear",
        "subtypes": ["General", "Sneakers", "Boots", "Flats"],
    },
    {
        "slug": ClothingCategory.ACCESSORIES,
        "label": "Accessories",
        "subtypes": ["General", "Bag", "Hat", "Scarf"],
    },
]


def get_wardrobe_categories():
    return WARDROBE_CATEGORIES


def valid_subtypes_for(category: ClothingCategory) -> list[str]:
    for entry in WARDROBE_CATEGORIES:
        if entry["slug"] == category:
            return entry["subtypes"]
    return []


def get_color_families() -> list[str]:
    return [color.value for color in ColorFamily]


def get_seasons() -> list[str]:
    return [season.value for season in Season]
