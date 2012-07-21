def str_to_dict(string):
    return dict((n, v) for n, v in (a.split('=') for a in string.split()))


def replies(func):
    def cb(obj, msg, *args, **kwargs):
        reply = func(obj, msg, *args, **kwargs)
        if reply:
            obj.write(reply, msg['from'])
    return cb
