from config import ADMIN_USERNAME

def is_admin(username):
    return username == ADMIN_USERNAME

def build_order_summary(items):
    total = sum(i["qty"] * i["price"] for i in items)
    lines = []
    for i in items:
        lines.append(f"{i['qty']}x {i['item']} - ${i['qty']*i['price']:.2f}")
    return "\n".join(lines), total

def build_admin_order_text(user_name, items):
    summary, total = build_order_summary(items)
    text = f"NEW ORDER FROM: {user_name}\n\n{summary}\n\nTOTAL: ${total:.2f}"
    return text, total
