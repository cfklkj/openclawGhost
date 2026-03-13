"""
加密解密模块
使用 Fernet (AES) 进行文件加密
"""
import os
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generate_key() -> bytes:
    """生成加密密钥"""
    return Fernet.generate_key()

def derive_key(password: str, salt: Optional[bytes] = None) -> tuple:
    """从密码派生加密密钥"""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = kdf.derive(password.encode())
    return Fernet(key), salt

class FileEncryptor:
    """文件加密器"""
    
    def __init__(self, key: Optional[bytes] = None):
        """
        初始化加密器
        
        Args:
            key: Fernet 密钥，如果为 None 则生成新密钥
        """
        self.key = key or generate_key()
        self.fernet = Fernet(self.key)
    
    def encrypt_file(self, input_path: str, output_path: str) -> bool:
        """
        加密文件
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
        
        Returns:
            是否成功
        """
        try:
            with open(input_path, 'rb') as f:
                data = f.read()
            
            encrypted = self.fernet.encrypt(data)
            
            with open(output_path, 'wb') as f:
                f.write(encrypted)
            
            return True
        except Exception as e:
            print(f"加密失败：{e}")
            return False
    
    def decrypt_file(self, input_path: str, output_path: str) -> bool:
        """
        解密文件
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
        
        Returns:
            是否成功
        """
        try:
            with open(input_path, 'rb') as f:
                encrypted = f.read()
            
            decrypted = self.fernet.decrypt(encrypted)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted)
            
            return True
        except Exception as e:
            print(f"解密失败：{e}")
            return False
    
    def save_key(self, key_path: str) -> bool:
        """保存密钥到文件"""
        try:
            with open(key_path, 'wb') as f:
                f.write(self.key)
            return True
        except Exception as e:
            print(f"保存密钥失败：{e}")
            return False
    
    @staticmethod
    def load_key(key_path: str) -> Optional[bytes]:
        """从文件加载密钥"""
        try:
            with open(key_path, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"加载密钥失败：{e}")
            return None
