def convert_to_utf8(li):
    """
    Take a list containing nested dictionaries and encode the dictionary values to unicode.

    :param li: list of nested dicts
    :type li: list
    :return: list of nested dicts
    :rtype: list
    """
    for item in li:
        # Check if item is a list
        if isinstance(item, list):
            # Run the function recursely on the list
            convert_to_utf8(item)
        # Check if item is a dict
        elif isinstance(item, dict):
            # Iterate over the keys in the dict
            for key, value in item.items():
                # Convert value to UTF8 and store to original key
                item[key] = value.encode('utf-8')
    return li
