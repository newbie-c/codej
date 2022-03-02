def parse_address(address):
    if len(address) > 30:
        name, domain = address.split('@')
        if len(domain) > 15:
            if len(name) > 14:
                domain = '~' + domain[-14:]
            else:
                tail = 30 - len(name) - 2
                domain = '~' + domain[-tail:]
        head = 30 - len(domain) - 2
        if len(name + '@' + domain) > 30:
            name = name[:head] + '~'
        return name + '@' + domain
    return address
