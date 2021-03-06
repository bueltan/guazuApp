from connection_endpoint import send_payload


def to_check(value, resolve, field):
    payload = '{"query": "{' + resolve + ' (' + field + ':\\"' + value + '\\"){'+field+'}}"}'
    json = send_payload(payload)
    print(payload)
    print(json)
    if json:
        if json['data'][resolve] is not None and not False:
            id = (json['data'][resolve][field])
            return id

    else:
        return json


def create_account(name, user, password, email):
    payload = '{"query": "mutation{createAccount(input:{name:\\"' + name + '\\",idName:\\"' + user + '\\",password:\\"' + password + '\\",email:\\"' + email + '\\"}){account{id}}}"}'
    json = send_payload(payload)
    if json is not None and not False:
        id = (json['data']['createAccount']['account']['id'])
        return id
    else:
        return json
