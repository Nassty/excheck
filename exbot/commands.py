from utils import replies


def get_command(cmd):
    return globals().get(cmd, lambda *x: '%s not found' % cmd)


@replies
def talk(obj, msg, *args, **kwargs):
    reply = 'already added'
    if msg['from'] not in obj.emails:
        obj.emails.append(msg['from'])
        reply = 'added to the alert watch'
    return reply


@replies
def watchlist(obj, msg, *args, **kwargs):
    reply = '\n'.join(["[%s]=>%s" % (x, y) for x, y in enumerate(obj.emails)])
    return reply


@replies
def remove(obj, msg, item, *args, **kwargs):
    try:
        index = int(item)
        if len(obj.emails) < index:
            return "the index %s does not exists" % index
        removed = obj.emails[index]
        del obj.emails[index]
        obj.write("you have been removed from the watchlist by %s"
                % msg['from'], removed)
        return '%s succesfully removed' % removed
    except ValueError:
        return "%s is not a number" % item
