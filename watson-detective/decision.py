import watson_developer_cloud

def gen_option(index, name, **values):
    out = {'key': index, 'name': name}
    for k, v in values.items():
        out.update({k: v})
    return out


def gen_preference(key, type, goal, full_name=None, is_objective=True, **values):
    """
    Generates a preference dictionary to add to the 'columns' key of the decision json
    :param key: informal (but official) name of the variable
    :param type: vartype (e.g., categorical or numeric)
    :param goal: max or min
    :param full_name: prettier name
    :param is_objective: false if reverse of goal is preferred
    :return: dictionary of preferences
    """

    out = {'key': key, 'type': type, 'full_name': full_name, 'goal': goal, 'is_objective': is_objective}
    for k, v in values.items():
        out.update({k: v})

    if type=="categorical":
        assert 'range' in values and 'preference' in values

    if

    return out

def