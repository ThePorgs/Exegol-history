import json


def format_into_txt(objects) -> str:
    output = ""

    for object in objects:
        for attribute in object:
            output += attribute
            output += "\n"

    return output


def format_into_csv(objects) -> str:
    output = ""

    for object in objects:
        for i, attribute in enumerate(object):
            output += attribute
            if i != (len(object) - 1):
                output += ","

        output += "\n"

    return output


def format_into_json(objects, field_names: [str]) -> str:
    output = []

    for object in objects:
        tmp = dict()
        i = 0

        for attribute in object:
            tmp[field_names[i].lower()] = attribute
            i += 1

        output.append(tmp)

    return json.dumps(output)
