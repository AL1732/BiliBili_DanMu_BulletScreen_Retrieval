# B站影视剧弹幕自动获取工具

一个用于自动获取B站官方影视剧弹幕的Python工具。

## 🎯 功能特点

- **简单易用**：只需输入ep_id即可获取弹幕
- **批量下载**：支持下载单个、多个或全部集数的弹幕
- **自动分类**：弹幕文件自动保存到以剧名命名的文件夹中
- **完整测试**：包含完整的单元测试套件

## 📁 项目结构

```
BiliBili_RollingTitleRetrieve/
├── src/
│   └── danmu_retriever_auto.py    # 主程序代码
├── tests/
│   └── test_danmu_retriever.py    # 单元测试
└── README.md                       # 项目说明文档
```

## 🚀 使用方法

### 1. 获取ep_id

1. 在B站打开任意一集视频
2. 从视频链接中找到ep_id
   - 例如：`https://www.bilibili.com/bangumi/play/ep403691`
   - ep_id就是 `403691` 或 `ep403691`

### 2. 运行脚本

```bash
python src/danmu_retriever_auto.py
```

### 3. 输入ep_id

按照提示输入ep_id，脚本会自动：
- 获取剧集信息
- 显示所有集数
- 询问要下载的集数

### 4. 选择集数

支持多种输入格式：
- **单个集数**：`1`
- **多个集数**：`1,2,3`
- **范围**：`1-5`
- **全部**：`all` 或 `全部`

### 5. 下载完成

弹幕文件会自动保存到以剧名命名的文件夹中，文件名格式为：
```
剧名_第X集_弹幕_CID.xml
```

## 🧪 运行测试

```bash
python tests/test_danmu_retriever.py
```

## 📋 依赖要求

- Python 3.6+
- 标准库（无需额外安装）

## ⚠️ 注意事项

- 本工具仅用于学习和研究目的
- 请遵守B站的使用条款和相关法律法规
- 弹幕文件仅供个人使用，请勿用于商业用途

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！
