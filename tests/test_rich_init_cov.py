from rich import print_json
import rich

def test_rich_print():
    print_json(data={"a": 1})
    rich.print("hello")
