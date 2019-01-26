# coding: utf-8
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import uuid
import hashlib


class Mytoken:
    def __init__(self):
        self.pwd = "feed5d47c860f422712ac902a89865db"

    def get_mac_address(self):
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])

    def generate_md5(self, data):
        m = hashlib.md5()
        m.update(data.encode())
        d = m.hexdigest()
        return d[:6]

    def gene_d(self):
        mac = self.get_mac_address()
        return self.generate_md5(mac)

    def generate_token(self, d, friends, timeout=3600 * 24):
        s = Serializer(self.pwd, expires_in=timeout)
        try:
            token = s.dumps({"mac": d, "friends": friends})
            return token.decode()
        except Exception as e:
            return None

    def dump_to_file(self, token):
        try:
            with open("token", "w") as f:
                f.write(token)
        except Exception as e:
            return None

    def load_token(self):
        try:
            with open("token", "r") as f:
                token = f.read()
            return token
        except Exception:
            return None

    def check_token(self, token):
        mac = self.get_mac_address()
        d = self.generate_md5(mac)
        s = Serializer("feed5d47c860f422712ac902a89865db")
        try:
            result = s.loads(token)
            if result.get("mac") != d:
                return False
            return result.get("friends")
        except Exception as e:
            return False

    def check(self):
        token = self.load_token()
        return self.check_token(token)


if __name__ == '__main__':
    mytoken = Mytoken()
    t = mytoken.generate_token("aaaaaa", [])
    print(t)
    mytoken.check_token(t)