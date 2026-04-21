class JsonPathUtil:

    @staticmethod
    def path_match(path: str, pattern: str):
        return JsonPathUtil.path_list_match(path.split('/'), pattern.split('/'))

    @staticmethod
    def path_list_match(path_parts: list[str], pattern_parts: list[str]):
        if len(path_parts) != len(pattern_parts):
            return None
        path_vars = {}
        for i in range(len(path_parts)):
            p = pattern_parts[i]
            e = path_parts[i]
            if p == '*':
                continue
            elif p.startswith('{') and p.endswith('}'):
                path_vars[p.removeprefix('{').removesuffix('}')] = e
            elif p != e:
                return None
        return path_vars

    @staticmethod
    def replace_path_vars(pattern: str, path_vars: dict[str, str]):
        parts = pattern.split('/')
        for i in range(len(parts)):
            p = parts[i]
            if p.startswith('{') and p.endswith('}'):
                parts[i] = path_vars[p.removeprefix('{').removesuffix('}')]
        return '/'.join(parts)

    @staticmethod
    def extract_path_variables(pattern: str):
        parts = pattern.split('/')
        path_vars = set()
        for i in range(len(parts)):
            p = parts[i]
            if p.startswith('{') and p.endswith('}'):
                path_vars.add(p.removeprefix('{').removesuffix('}'))
        return path_vars
