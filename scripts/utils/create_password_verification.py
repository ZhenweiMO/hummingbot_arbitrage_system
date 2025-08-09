#!/usr/bin/env python3
"""
创建 Hummingbot 密码验证文件的脚本
"""

import sys
import os
sys.path.append('./hummingbot')

from hummingbot.client.config.config_crypt import ETHKeyFileSecretManger, store_password_verification

def create_password_verification(password: str, output_path: str):
    """创建密码验证文件"""
    try:
        # 创建 secrets manager
        secrets_manager = ETHKeyFileSecretManger(password)
        
        # 存储密码验证
        store_password_verification(secrets_manager)
        
        print(f"✅ 密码验证文件已创建: {output_path}")
        print(f"📝 使用的密码: {password}")
        
    except Exception as e:
        print(f"❌ 创建密码验证文件失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    password = "test1234"
    output_path = "./hummingbot/conf/.password_verification"
    
    print("🔐 创建 Hummingbot 密码验证文件")
    print("=" * 50)
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 创建密码验证文件
    success = create_password_verification(password, output_path)
    
    if success:
        print("\n🎉 密码验证文件创建成功！")
        print("现在可以启动 Hummingbot 了。")
    else:
        print("\n💥 密码验证文件创建失败！")
        sys.exit(1) 