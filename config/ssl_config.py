"""SSL configuration"""

import ssl
from app.config.environment import env_config

class SSLConfig:
    """SSL configuration for the application"""
    
    def __init__(self):
        self.enabled = env_config.SSL_ENABLED
        self.cert_file = env_config.SSL_CERT_FILE
        self.key_file = env_config.SSL_KEY_FILE
    
    def get_ssl_context(self):
        """Get SSL context if SSL is enabled"""
        if not self.enabled:
            return None
        
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        if self.cert_file and self.key_file:
            context.load_cert_chain(self.cert_file, self.key_file)
        
        return context

ssl_config = SSLConfig()