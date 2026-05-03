#!/usr/bin/env python3
"""
调试牌组创建
"""
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from models.tarot_card import TarotCard, SuitType, ArcanaType
    print("✓ 成功导入模型")
except Exception as e:
    print(f"✗ 导入模型失败: {e}")
    sys.exit(1)

try:
    from data.tarot_deck import create_standard_deck
    print("✓ 成功导入牌组函数")
except Exception as e:
    print(f"✗ 导入牌组函数失败: {e}")
    sys.exit(1)

try:
    print("开始创建牌组...")
    deck = create_standard_deck()
    print(f"牌组创建完成，总数: {len(deck)}")
    
    # 分析牌组构成
    major_count = 0
    minor_count = 0
    
    for card in deck:
        if card.arcana == ArcanaType.MAJOR:
            major_count += 1
        else:
            minor_count += 1
    
    print(f"大阿卡纳: {major_count}")
    print(f"小阿卡纳: {minor_count}")
    
    # 显示前几张牌
    print("\n前5张牌:")
    for i, card in enumerate(deck[:5]):
        print(f"{i+1}. {card.name} ({card.suit.value}, {card.arcana.value})")
    
except Exception as e:
    print(f"✗ 创建牌组失败: {e}")
    import traceback
    traceback.print_exc()