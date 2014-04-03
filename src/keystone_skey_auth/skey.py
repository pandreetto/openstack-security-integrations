import base64

from keystone import identity
from keystone.auth import AuthMethodHandler
from keystone.openstack.common import log as logging
from keystone.exception import Unauthorized, UserNotFound, NotFound

from Crypto.Cipher import AES
from oslo.config import cfg

METHOD_NAME = 'sKey'

LOG = logging.getLogger(__name__)

#
# TODO
# investigate OTP libraries
# https://github.com/nathforge/pyotp
# investigate schema based on timestamp and originatorID
# originatorID is the uniqueID of the thread sending the request.
#
# move token in the body
# use json for token content
#

class SecretKeyAuth(AuthMethodHandler):

    def __init__(self):
        cfg.CONF.register_opt(cfg.StrOpt('secret_key', default=None), group='skey')
        self.identity_api = identity.Manager()
        
        self.aes_key = cfg.CONF.skey.secret_key
        if len(self.aes_key) > 32:
            self.aes_key = self.aes_key[:32]
        elif len(self.aes_key) > 16:
            self.aes_key = self.aes_key[:16]
        elif len(self.aes_key) > 8:
            self.aes_key = self.aes_key[:8]
        else:
            self.aes_key = None
    
    def _parse_cryptoken(self, data):
        if self.aes_key == None:
            raise Exception("Wrong secret key")

        cipher = AES.new(self.aes_key, AES.MODE_CFB)
        b64msg = base64.b64decode(data)
        return cipher.decrypt(b64msg)[256:]
        
    
    def authenticate(self, context, auth_info, auth_context):
        headers = context['headers']
        if 'X-Auth-Secret' in headers and 'user_id' not in auth_context:
            try:
                
                fqun = self._parse_cryptoken(headers['X-Auth-Secret'])
                LOG.info("Accepted secret for " + fqun)
                
                user_name, domain_name = fqun.split('|')
                
                uDict = self.identity_api.get_user_by_name(user_name, domain_name)
                dDict = self.identity_api.get_domain_by_name(domain_name)
                
                if not uDict['enabled']:
                    raise Unauthorized("User %s is disabled" % uDict['name'])
                if not dDict['enabled']:
                    raise Unauthorized("Domain %s is disabled" % dDict['name'])
                
                auth_context['user_id'] = uDict['id']
                return None
            except UserNotFound:
                raise NotFound("Missing user")
            except Unauthorized as noAuthEx:
                LOG.warning(str(noAuthEx))
                raise
            except Exception:
                LOG.error("Cannot decrypt token", exc_info=True)
        
        raise Unauthorized('Cannot authenticate using sKey')

'''
## Example of API call with fqun "andreett|default"

POST /v3/auth/tokens HTTP/1.1
Host: 193.206.210.223:5000
Content-Length: 61
Accept-Encoding: gzip, deflate, compress
Accept: */*
User-Agent: python-keystoneclient
X-Auth-Secret: DAnjHuV16dh4hXGCm/uk9A==
Content-Type: application/json

{"auth" : {"identity" : {"methods" : ["sKey"], "sKey" : {}}}}
'''


