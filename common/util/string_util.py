import re

PATTERN_NAME = "\${(.*?)"
PATTERN_PARAMS = "#{(.*?)}"

def matchReplace(pattern, target, kwargs):
    matchs = re.findall(pattern, target)
    result = target
    if matchs:
        for match in matchs:
            result = result.replace("${" + match + "}", kwargs[match])
    return result

def matchParams(pattern, target, kwargs):
    matchs = re.findall(pattern, target)
    result = []
    result_target = target
    if matchs:
        for match in matchs:
            result.append(kwargs[match])
            result_target = result_target.replace("#{" + match + "}", "%s")
    return result_target, result