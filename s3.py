# -*- coding: utf-8 -*-

import json
import base64
import hmac
import hashlib


def sign_policy(policy, secret_key):
    policy_string = base64.encodestring(json.dumps(policy)).replace('\n', '').strip()
    signature = hmac.new(secret_key, policy_string, hashlib.sha1).digest()
    signature = base64.b64encode(signature).replace('\n', '').strip()
    return (policy_string, signature)
