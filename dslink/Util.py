import base64


def base64_encode(data):
    return base64.urlsafe_b64encode(data).rstrip("=")


def base64_decode(data):
    return base64.urlsafe_b64decode(base64_add_padding(data))


def base64_add_padding(string):
    """
    Add padding to a URL safe base64 string.
    :param string: Non-padded Url-safe Base64 string.
    :return: Padded Url-safe Base64 string.
    """
    while len(string) % 4 != 0:
        string += "="
    return string
