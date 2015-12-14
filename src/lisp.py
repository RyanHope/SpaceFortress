class symbol(object):
    def __init__(self,obj):
        self.name = str(obj)

    def __repr__(self):
        return '<symbol "%s">'%self.name

def lispify(obj):
    if isinstance(obj, str):
        return '"' + obj.replace('"','\"') + '"'
    if isinstance(obj, unicode):
        return ('"' + obj.replace('"','\"') + '"')
    #elif isinstance(obj, none):
    #return 'nil'
    elif isinstance(obj,bool):
        return 't' if obj else 'nil'
    elif isinstance(obj,int):
        return str(obj)
    elif isinstance(obj,float):
        return str(obj)
    elif isinstance(obj,list):
        return '(' + ' '.join(map(lispify,obj)) + ')'
    elif isinstance(obj,symbol):
        return ':' + obj.name
    elif isinstance(obj,dict):
        acc = []
        for k,v in obj.iteritems():
            acc.append(symbol(k))
            acc.append(v)
        return lispify(acc)
    elif obj == None:
        return 'nil'
    else:
        raise Exception("Cannot lispify %s"%unicode(obj))
