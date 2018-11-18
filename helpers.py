def every(iterable, callback):
    for item in iterable:
        if(not callback(item)):
            return False
    return True

def some(iterable, callback):
    for item in iterable:
        if(callback(item)):
            return True 
    return False

def first(iterable, callback):
    for item in iterable:
        if(callback(item)):
            return item
    return None