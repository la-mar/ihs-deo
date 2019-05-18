
def from_file(filename: str) -> str:
    xml = None
    with open(filename, "r") as f :
        xml = f.read().splitlines()
    return ''.join(xml)

def to_file(xml: str, filename: str) -> str:
    with open(filename, "w") as f:
        f.writelines(xml)

# decorator
def chained(func):
    """Capture the analysis method"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        # print(f"Calling {func.__name__}({signature})")
        obj = args[0]
        if not hasattr(obj, '_chain'):
            obj._chain = []
        if hasattr(obj, 'norm'):
            obj._chain.append((obj.norm, func.__name__))
        else:
            obj._chain.append((None, func.__name__))
        value = func(*args, **kwargs)
        if isinstance(value, pd.Series):
            if not value.empty:
                value['method'] = f'operator.classifier.{func.__name__}'
        return value
    return wrapper