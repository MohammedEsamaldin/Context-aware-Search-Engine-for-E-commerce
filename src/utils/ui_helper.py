import re



def category_icon(title):
    title = title.lower()
    if "dress" in title: return "👗"
    if "blanket" in title or "swaddle" in title: return "🛌"
    if "headband" in title: return "🎀"
    if "crib" in title or "toy" in title: return "🧸"
    return "🍼"