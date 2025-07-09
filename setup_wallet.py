#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钱包配置脚本
用于快速设置Hyperliquid资金费率套利系统的钱包
"""

import json
import os
from wallet_simple import SimpleWalletManager

def setup_wallet():
    """设置钱包"""
    print("="*50)
    print("Hyperliquid资金费率套利系统 - 钱包配置")
    print("="*50)
    
    # 创建钱包管理器
    wallet = SimpleWalletManager()
    
    # 检查是否已有配置文件
    if os.path.exists("wallet.json"):
        print("发现现有钱包配置文件 wallet.json")
        choice = input("是否要加载现有配置？(y/n): ").strip().lower()
        
        if choice == 'y':
            if wallet.load_config():
                print("✅ 成功加载现有钱包配置")
                balance, margin = wallet.get_balance()
                print(f"钱包地址: {wallet.wallet_info['address']}")
                print(f"当前余额: {balance} USDT")
                print(f"可用保证金: {margin} USDT")
                return True
            else:
                print("❌ 加载配置失败，将重新配置")
    
    print("\n请按照以下步骤配置钱包：")
    print("1. 确保你有MetaMask或其他Web3钱包")
    print("2. 准备钱包地址和私钥")
    print("3. 确保钱包中有足够的USDT余额")
    print()
    
    # 获取钱包地址
    while True:
        address = input("请输入钱包地址 (0x开头): ").strip()
        
        if not address.startswith('0x'):
            print("❌ 钱包地址必须以0x开头")
            continue
            
        if len(address) != 42:
            print("❌ 钱包地址长度不正确，应该是42位字符")
            continue
            
        break
    
    # 获取私钥
    while True:
        private_key = input("请输入私钥 (0x开头，64位十六进制): ").strip()
        
        if not private_key.startswith('0x'):
            print("❌ 私钥必须以0x开头")
            continue
            
        if len(private_key) != 66:  # 0x + 64位十六进制
            print("❌ 私钥长度不正确，应该是66位字符")
            continue
            
        break
    
    # 确认信息
    print("\n请确认以下信息：")
    print(f"钱包地址: {address}")
    print(f"私钥: {private_key[:10]}...{private_key[-10:]}")
    
    confirm = input("\n信息是否正确？(y/n): ").strip().lower()
    if confirm != 'y':
        print("配置已取消")
        return False
    
    # 连接钱包
    print("\n正在连接钱包...")
    if wallet.connect_wallet(address, private_key):
        print("✅ 钱包连接成功！")
        
        # 保存配置
        if wallet.save_config():
            print("✅ 钱包配置已保存到 wallet.json")
        else:
            print("❌ 保存配置失败")
            return False
        
        # 显示余额信息
        balance, margin = wallet.get_balance()
        print(f"\n钱包信息：")
        print(f"地址: {address}")
        print(f"余额: {balance} USDT")
        print(f"可用保证金: {margin} USDT")
        
        return True
    else:
        print("❌ 钱包连接失败，请检查地址和私钥")
        return False

def main():
    """主函数"""
    print("Hyperliquid资金费率套利系统 - 钱包配置")
    print("="*50)
    
    if setup_wallet():
        print("\n🎉 钱包配置完成！现在可以运行主系统了")
        print("运行命令: python hyperliquid_system.py")
    else:
        print("\n❌ 钱包配置失败")

if __name__ == "__main__":
    main() 