def extract_chapter_number(text):
    original = text
    chapter_number = ""
    text = text.lower()
    text = text.strip().replace(" ", "")
    if "href" in text:
        href = text[text.find("href"):text.find('">')]
        text = text.replace(href, "")
    if "chapter" in text:
        text = text[text.find("chapter"):]
    elif "ch" in text:
        text = text[text.find("ch"):]

    num_chars = "0123456789."
    found_a_number = False
    for char in text:
        if char in num_chars and not (char == "." and not found_a_number):
            found_a_number = True
            chapter_number += char
        elif char not in num_chars and found_a_number:
            break

    if not found_a_number:
        return f"Did not find a number in chapter text, extracted - *{chapter_number}*\n" \
               f"Original: {original}"
    else:
        try:
            return float(chapter_number)
        except ValueError as e:
            return f"ValueError in extracting chapter number, extracted - *{chapter_number}*\n" \
                   f"Original: {original}" \
                   f"Exception {e}"
