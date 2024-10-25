import re


class NotFoundKeyException(Exception):
    pass


def get_value_by_nested_key(data, key, is_required=False):
    value = data
    if key is None:
        if is_required:
            raise NotFoundKeyException(f"Key {key} is required")
        return None
    for k in key.split("/"):
        value = value.get(k)
        if value is None and is_required:
            raise NotFoundKeyException(f"Key {k} is not valid")
    return value


def remove_html_tags(text=None):
    if text is None:
        return None
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def remove_tiki_text_extension(text=None):
    if text is None:
        return None
    text = text.split("Giá sản phẩm trên Tiki đã bao gồm thuế theo luật hiện hành.")[0]
    return text
