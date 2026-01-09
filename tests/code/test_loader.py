from data.code_loader import CodeLoader

def test_file_loader():
    print("=== Testing FileCodeLoader ===")
    loader = CodeLoader.create("file")
    code = loader.load("tests/test_loader_sample.py")
    print(code)
    print()

def test_text_loader():
    print("=== Testing TextInputCodeLoader ===")
    loader = CodeLoader.create("text")
    code = loader.load("print('hello from text input')")
    print(code)
    print()

if __name__ == "__main__":
    test_file_loader()
    test_text_loader()
