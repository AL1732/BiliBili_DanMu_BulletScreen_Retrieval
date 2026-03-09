#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站影视剧弹幕自动获取工具 - 单元测试
"""

import unittest
import unittest.mock
import os
import sys
import json
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.danmu_retriever_auto import parse_episode_selection


class TestParseEpisodeSelection(unittest.TestCase):
    """测试parse_episode_selection函数"""
    
    def test_single_episode(self):
        """测试单个集数"""
        result = parse_episode_selection("1", 10)
        self.assertEqual(result, [1])
        
        result = parse_episode_selection("5", 10)
        self.assertEqual(result, [5])
    
    def test_multiple_episodes(self):
        """测试多个集数（逗号分隔）"""
        result = parse_episode_selection("1,2,3", 10)
        self.assertEqual(result, [1, 2, 3])
        
        result = parse_episode_selection("1,3,5", 10)
        self.assertEqual(result, [1, 3, 5])
        
        result = parse_episode_selection("3,1,2", 10)
        self.assertEqual(result, [1, 2, 3])
    
    def test_range_episodes(self):
        """测试范围（1-5）"""
        result = parse_episode_selection("1-5", 10)
        self.assertEqual(result, [1, 2, 3, 4, 5])
        
        result = parse_episode_selection("3-7", 10)
        self.assertEqual(result, [3, 4, 5, 6, 7])
    
    def test_all_episodes(self):
        """测试全部集数"""
        result = parse_episode_selection("all", 10)
        self.assertEqual(result, list(range(1, 11)))
        
        result = parse_episode_selection("全部", 10)
        self.assertEqual(result, list(range(1, 11)))
        
        result = parse_episode_selection("ALL", 10)
        self.assertEqual(result, list(range(1, 11)))
    
    def test_out_of_range(self):
        """测试超出范围"""
        result = parse_episode_selection("15", 10)
        self.assertIsNone(result)
        
        result = parse_episode_selection("0", 10)
        self.assertIsNone(result)
        
        result = parse_episode_selection("1-15", 10)
        self.assertIsNone(result)
    
    def test_invalid_input(self):
        """测试无效输入"""
        result = parse_episode_selection("abc", 10)
        self.assertIsNone(result)
        
        result = parse_episode_selection("abc,xyz", 10)
        self.assertIsNone(result)
        
        result = parse_episode_selection("1-abc", 10)
        self.assertIsNone(result)
    
    def test_duplicate_episodes(self):
        """测试重复集数"""
        result = parse_episode_selection("1,2,2,3", 10)
        self.assertEqual(result, [1, 2, 3])
    
    def test_whitespace_handling(self):
        """测试空格处理"""
        result = parse_episode_selection(" 1 , 2 , 3 ", 10)
        self.assertEqual(result, [1, 2, 3])
        
        result = parse_episode_selection(" 1 - 5 ", 10)
        self.assertEqual(result, [1, 2, 3, 4, 5])


class TestGetSeasonInfoByEpId(unittest.TestCase):
    """测试get_season_info_by_ep_id函数"""
    
    @unittest.mock.patch('src.danmu_retriever_auto.urllib.request.urlopen')
    def test_successful_request(self, mock_urlopen):
        """测试成功请求"""
        from src.danmu_retriever_auto import get_season_info_by_ep_id
        
        mock_response = unittest.mock.MagicMock()
        mock_response.read.return_value = json.dumps({
            'code': 0,
            'result': {
                'season_id': 12345,
                'title': 'Test Series',
                'episodes': [
                    {'id': 1, 'title': '1', 'cid': 1001},
                    {'id': 2, 'title': '2', 'cid': 1002}
                ]
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = get_season_info_by_ep_id("403691")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['code'], 0)
        self.assertEqual(result['result']['season_id'], 12345)
        self.assertEqual(result['result']['title'], 'Test Series')
        self.assertEqual(len(result['result']['episodes']), 2)
    
    @unittest.mock.patch('src.danmu_retriever_auto.urllib.request.urlopen')
    def test_failed_request(self, mock_urlopen):
        """测试失败请求"""
        from src.danmu_retriever_auto import get_season_info_by_ep_id
        
        mock_urlopen.side_effect = Exception("Network error")
        
        result = get_season_info_by_ep_id("403691")
        
        self.assertIsNone(result)
    
    @unittest.mock.patch('src.danmu_retriever_auto.urllib.request.urlopen')
    def test_api_error(self, mock_urlopen):
        """测试API返回错误"""
        from src.danmu_retriever_auto import get_season_info_by_ep_id
        
        mock_response = unittest.mock.MagicMock()
        mock_response.read.return_value = json.dumps({
            'code': -1,
            'message': 'Not found'
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = get_season_info_by_ep_id("403691")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['code'], -1)


class TestDownloadDanmu(unittest.TestCase):
    """测试download_danmu函数"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @unittest.mock.patch('src.danmu_retriever_auto.urllib.request.urlopen')
    def test_successful_download(self, mock_urlopen):
        """测试成功下载"""
        from src.danmu_retriever_auto import download_danmu
        
        mock_response = unittest.mock.MagicMock()
        mock_response.read.return_value = b'<?xml version="1.0" encoding="utf-8"?><i><d p="0.0,1,25,16777215,1234567890,0,0,0">Test Danmu</d></i>'
        mock_response.headers.get.return_value = ''
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = download_danmu("123456", "Test Series", "1", self.test_dir)
        
        self.assertTrue(result)
        expected_file = os.path.join(self.test_dir, "Test Series_第1集_弹幕_123456.xml")
        self.assertTrue(os.path.exists(expected_file))
    
    @unittest.mock.patch('src.danmu_retriever_auto.urllib.request.urlopen')
    def test_deflate_compressed_download(self, mock_urlopen):
        """测试deflate压缩下载"""
        from src.danmu_retriever_auto import download_danmu
        import zlib
        
        xml_content = b'<?xml version="1.0" encoding="utf-8"?><i><d p="0.0,1,25,16777215,1234567890,0,0,0">Test Danmu</d></i>'
        compressed_content = zlib.compress(xml_content)
        
        mock_response = unittest.mock.MagicMock()
        mock_response.read.return_value = compressed_content
        mock_response.headers.get.return_value = 'deflate'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = download_danmu("123456", "Test Series", "1", self.test_dir)
        
        self.assertTrue(result)
        expected_file = os.path.join(self.test_dir, "Test Series_第1集_弹幕_123456.xml")
        self.assertTrue(os.path.exists(expected_file))
    
    @unittest.mock.patch('src.danmu_retriever_auto.urllib.request.urlopen')
    def test_http_error(self, mock_urlopen):
        """测试HTTP错误"""
        from src.danmu_retriever_auto import download_danmu
        from urllib.error import HTTPError
        
        mock_urlopen.side_effect = HTTPError(
            "https://api.bilibili.com/x/v1/dm/list.so?oid=123456",
            404,
            "Not Found",
            {},
            None
        )
        
        result = download_danmu("123456", "Test Series", "1", self.test_dir)
        
        self.assertFalse(result)
    
    @unittest.mock.patch('src.danmu_retriever_auto.urllib.request.urlopen')
    def test_invalid_xml_content(self, mock_urlopen):
        """测试无效XML内容"""
        from src.danmu_retriever_auto import download_danmu
        
        mock_response = unittest.mock.MagicMock()
        mock_response.read.return_value = b'This is not XML'
        mock_response.headers.get.return_value = ''
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = download_danmu("123456", "Test Series", "1", self.test_dir)
        
        self.assertFalse(result)
    
    def test_filename_sanitization(self):
        """测试文件名清理"""
        from src.danmu_retriever_auto import download_danmu
        
        with unittest.mock.patch('src.danmu_retriever_auto.urllib.request.urlopen') as mock_urlopen:
            mock_response = unittest.mock.MagicMock()
            mock_response.read.return_value = b'<?xml version="1.0" encoding="utf-8"?><i><d p="0.0,1,25,16777215,1234567890,0,0,0">Test Danmu</d></i>'
            mock_response.headers.get.return_value = ''
            mock_urlopen.return_value.__enter__.return_value = mock_response
            
            download_danmu("123456", "Test:Series/Special|Chars", "1", self.test_dir)
            
            files = os.listdir(self.test_dir)
            self.assertTrue(any('Test_Series_Special_Chars' in f for f in files))


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)


def run_tests():
    """运行所有测试"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    run_tests()
