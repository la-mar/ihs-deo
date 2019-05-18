
def from_file(filename: str) -> str:
    xml = None
    with open(filename, "r") as f :
        xml = f.read().splitlines()
    return ''.join(xml)

def to_file(xml: str, filename: str) -> str:
    with open(filename, "w") as f:
        f.writelines(xml)