#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站影视剧弹幕自动获取工具
支持通过ep_id自动获取cid并下载弹幕
支持批量下载：单个集数、多个集数、全部
"""

import os
import sys
import re
import json
import urllib.request
import zlib
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def print_separator():
    print("=" * 60)


def print_welcome():
    print_separator()
    print("🎬 B站影视剧弹幕自动获取工具")
    print_separator()
    print("使用方法：")
    print("  1. 在B站打开任意一集，找到ep_id")
    print("     例如：https://www.bilibili.com/bangumi/play/ep403691")
    print("     ep_id就是 403691")
    print("  2. 将ep_id输入到本工具")
    print("  3. 工具会自动获取该剧集的所有集数")
    print("  4. 选择要下载的集数（单个、多个、全部）")
    print("  5. 弹幕会自动下载到以剧名命名的文件夹中")
    print_separator()


def get_season_info_by_ep_id(ep_id):
    """通过ep_id获取season信息"""
    api_url = f"https://api.bilibili.com/pgc/view/web/season?ep_id={ep_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.bilibili.com/',
    }
    
    try:
        request = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        return None


def download_danmu(cid, title, episode_number, output_dir):
    """下载弹幕XML文件"""
    url = f"https://api.bilibili.com/x/v1/dm/list.so?oid={cid}"
    
    safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)
    filename = f"{safe_title}_第{episode_number}集_弹幕_{cid}.xml"
    filepath = os.path.join(output_dir, filename)
    
    print(f"\n📥 正在下载第 {episode_number} 集弹幕...")
    print(f"   cid: {cid}")
    print(f"   保存路径: {filepath}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        request = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read()
            
            # 检查是否需要解压
            encoding = response.headers.get('Content-Encoding', '')
            if 'deflate' in encoding:
                try:
                    content = zlib.decompress(content, -zlib.MAX_WBITS)
                except:
                    try:
                        content = zlib.decompress(content)
                    except:
                        pass
            
            if b'<?xml' in content[:100] or b'<i>' in content[:100]:
                with open(filepath, 'wb') as f:
                    f.write(content)
                
                file_size = os.path.getsize(filepath)
                print(f"   ✅ 下载成功！文件大小: {file_size / 1024:.2f} KB")
                return True
            else:
                print(f"   ❌ 下载的内容不是有效的弹幕XML文件")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"   ❌ HTTP错误：{e.code} - {e.reason}")
        if e.code == 404:
            print("      提示：CID不正确或该视频没有弹幕")
        elif e.code == 403:
            print("      提示：访问被拒绝，可能需要登录")
        return False
    except Exception as e:
        print(f"   ❌ 下载失败：{str(e)}")
        return False


def parse_episode_selection(input_str, total_episodes):
    """解析用户输入的集数选择"""
    input_str = input_str.strip().lower()
    
    # 全部
    if input_str in ['all', '全部', 'all']:
        return list(range(1, total_episodes + 1))
    
    # 单个集数
    if input_str.isdigit():
        episode_num = int(input_str)
        if 1 <= episode_num <= total_episodes:
            return [episode_num]
        else:
            print(f"   ❌ 集数超出范围（1-{total_episodes}）")
            return None
    
    # 多个集数（逗号分隔）
    if ',' in input_str:
        episodes = []
        for part in input_str.split(','):
            part = part.strip()
            if part.isdigit():
                episode_num = int(part)
                if 1 <= episode_num <= total_episodes:
                    episodes.append(episode_num)
                else:
                    print(f"   ❌ 集数 {episode_num} 超出范围（1-{total_episodes}）")
                    return None
        if episodes:
            return sorted(list(set(episodes)))
        return None
    
    # 范围（如：1-5）
    if '-' in input_str:
        parts = input_str.split('-')
        if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
            start = int(parts[0].strip())
            end = int(parts[1].strip())
            if 1 <= start <= total_episodes and 1 <= end <= total_episodes:
                return list(range(start, end + 1))
            else:
                print(f"   ❌ 范围超出（1-{total_episodes}）")
                return None
    
    print(f"   ❌ 输入格式错误")
    print(f"      支持的格式：")
    print(f"      - 单个集数：1")
    print(f"      - 多个集数：1,2,3")
    print(f"      - 范围：1-5")
    print(f"      - 全部：all 或 全部")
    return None


def main():
    """主函数"""
    print_welcome()
    
    while True:
        print_separator()
        print("\n📝 请输入ep_id（从B站视频链接中获取）")
        print("   例如：https://www.bilibili.com/bangumi/play/ep403691")
        print("   ep_id就是 403691 或 ep403691")
        print("-" * 60)
        
        ep_id_input = input("请输入ep_id（支持数字或ep+数字格式）：").strip()
        ep_id = re.sub(r'[^0-9]', '', ep_id_input)
        
        if not ep_id:
            print("   ❌ 输入无效，请输入数字")
            continue
        
        # 获取season信息
        season_data = get_season_info_by_ep_id(ep_id)
        
        if not season_data or season_data.get('code') != 0:
            print("   ❌ 未找到该ep_id对应的剧集，请检查ep_id是否正确")
            continue
        
        result = season_data.get('result', {})
        episodes = result.get('episodes', [])
        season_id = result.get('season_id')
        title = result.get('title', '')
        
        print(f"\n✅ 找到剧集: {title}")
        print(f"   season_id: {season_id}")
        print(f"   总集数: {len(episodes)}")
        
        # 显示所有集数
        print(f"\n所有集数:")
        for i, ep in enumerate(episodes):
            print(f"   {i+1:2d}. 第{ep.get('title')}集 (ep_id={ep.get('id')}, cid={ep.get('cid')})")
        
        # 询问用户要下载哪些集数
        print_separator()
        print(f"\n📥 请选择要下载的集数")
        print(f"   支持的格式：")
        print(f"   - 单个集数：1")
        print(f"   - 多个集数：1,2,3")
        print(f"   - 范围：1-5")
        print(f"   - 全部：all 或 全部")
        print("-" * 60)
        
        episode_selection = input("请输入要下载的集数：").strip()
        
        # 解析用户输入
        episodes_to_download = parse_episode_selection(episode_selection, len(episodes))
        
        if not episodes_to_download:
            continue
        
        # 创建输出文件夹
        safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), safe_title)
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"\n📁 创建文件夹: {output_dir}")
        
        # 下载弹幕
        print_separator()
        print(f"\n准备下载 {len(episodes_to_download)} 集的弹幕...")
        print(f"📁 保存位置: {output_dir}")
        print_separator()
        
        success_count = 0
        fail_count = 0
        
        for episode_num in episodes_to_download:
            # 查找对应的集数信息
            episode_info = None
            for ep in episodes:
                if ep.get('title') == str(episode_num):
                    episode_info = ep
                    break
            
            if not episode_info:
                print(f"\n❌ 未找到第 {episode_num} 集")
                fail_count += 1
                continue
            
            cid = episode_info.get('cid')
            success = download_danmu(cid, title, episode_num, output_dir)
            
            if success:
                success_count += 1
            else:
                fail_count += 1
        
        # 显示下载结果
        print_separator()
        print(f"\n� 下载完成！")
        print(f"   成功: {success_count} 集")
        print(f"   失败: {fail_count} 集")
        
        # 询问是否继续
        print_separator()
        choice = input("\n是否继续下载其他剧集的弹幕？(y/n）：").strip().lower()
        if choice != 'y':
            print("\n👋 感谢使用，再见！")
            break
        print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作，程序已退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序发生错误：{str(e)}")
        sys.exit(1)
