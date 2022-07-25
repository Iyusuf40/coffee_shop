import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
import jose
from urllib.request import urlopen


AUTH0_DOMAIN = 'yusuf-fsnd-udacity.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'drinks'

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''


def get_token_auth_header():
    header = request.headers
    if not header:
        raise AuthError({"code": "headers not found"}, 401)

    authorization = header.get("Authorization")
    if not authorization:
        raise AuthError({"code": "authorization not found"}, 401)

    parts = authorization.split()
    if len(parts) != 2:
        raise AuthError({"code": "invalid authorization"}, 401)

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid authorization",
                         "description": "expect Bearer "
                         "<token> as authorization"}, 401)
    # token = parts[1].split(".")[1]

    token = parts[1]
    return token


'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not
    included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission
    string is not in the payload permissions array
    return true otherwise
'''


def check_permissions(permission, payload):
    for item in payload["permissions"]:
        if item == permission:
            return True
    raise AuthError({"code": "permission check fail"}, 401)


'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here:
    https://stackoverflow.com/questions/50236117/scraping-ssl-
    certificate-verify-failed-error-for-http-en-wikipedia-org
'''


def verify_decode_jwt(token):
    token_head = jwt.get_unverified_header(token)
    if not token_head.get("kid"):
        raise AuthError({"code": "invalid token",
                         "description": "token has no id"},
                        401)
    json_res = urlopen("https://" + AUTH0_DOMAIN +
                       "/.well-known/jwks.json")
    public_keys = json.loads(json_res.read())

    decoding_key = {}
    for key in public_keys["keys"]:
        if key["kid"] == token_head["kid"]:
            decoding_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
    if decoding_key:
        try:
            verified_token = jwt.decode(token,
                                        decoding_key,
                                        algorithms=ALGORITHMS,
                                        audience=API_AUDIENCE,
                                        issuer="https://" +
                                        "" + AUTH0_DOMAIN + "/"
                                        )
        except jwt.ExpiredSignatureError:
            raise AuthError({"code": "token expired"},
                            401)
        except jwt.JWTClaimsError:
            raise AuthError({"code": "claims failed"
                             " verification"}, 401)
        except Exception:
            raise AuthError({"code": "invalid_header"},
                            401)
    _request_ctx_stack.top.current_user = verified_token
    return verified_token


'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate
    claims and check the requested permission
    return the decorator which passes the decoded payload to
    the decorated method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
