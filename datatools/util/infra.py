def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            wrapper.cached_result = f(*args, **kwargs)
        return wrapper.cached_result
    wrapper.has_run = False
    return wrapper
