import pyparsing as pp

WRITTEN_BY_TOK = "WRITTEN BY"
WRITTEN_BEFORE_TOK = "WRITTEN BEFORE"
WRITTEN_AFTER_TOK = "WRITTEN AFTER"
BIAS_TOK = "HAVING BIAS"
PUBLISHED_BY_TOK = "PUBLISHED BY"
AND_TOKEN = "AND"

ratings_tok_dict = {
    "LEFT": "LEFT",
    "LEAN LEFT": "LEAN_LEFT",
    "CENTER": "CENTER",
    "LEAN RIGHT": "LEAN_RIGHT",
    "RIGHT": "RIGHT",
    "MIXED": "MIXED"
}

author = pp.QuotedString("\"")
additional_author = "AND" + author
author_list = pp.Group(author + additional_author[...])
author_string = pp.Group("WRITTEN BY" + author_list)
before_string = pp.Group("WRITTEN BEFORE" + pp.Regex("[0-9]{1,2}-[0-9]{1,2}-[0-9]{4}"))
after_string = pp.Group("WRITTEN AFTER" + pp.Regex("[0-9]{1,2}-[0-9]{1,2}-[0-9]{4}"))

left_ident = pp.Word("LEFT")
lean_left_ident = pp.Word("LEAN LEFT")
center_ident = pp.Word("CENTER")
lean_right_ident = pp.Word("LEAN RIGHT")
right_ident = pp.Word("RIGHT")
mixed_ident = pp.Word("MIXED")
bias_rating = left_ident ^ lean_left_ident ^ center_ident ^ lean_right_ident ^ right_ident ^ mixed_ident
bias_string = pp.Group("HAVING BIAS" + bias_rating)

news_source = pp.QuotedString("\"")
news_source_string = pp.Group("PUBLISHED BY" + news_source)

query_condition = author_string ^ before_string ^ after_string ^ news_source_string ^ bias_string
condition_list = "`" + query_condition[1, ...] + "`"


if __name__ == "__main__":
    string = "`WRITTEN BEFORE 5-5-2020 WRITTEN AFTER 12-12-2020`"
    tree = condition_list.parseString(string)
    print(tree)