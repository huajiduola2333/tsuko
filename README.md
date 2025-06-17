
# 项目名称：Tsukoつこ

## 简介

Tsukoつこ是一个 Python 项目，旨在自动化处理来自深圳技术大学（SZTU）公文通的通知信息。它能够抓取最新的通知，使用 AI 对通知进行分类和总结，并以友好的格式展示给用户。

## 主要功能

- **通知抓取**：从深圳技术大学官网（教务处、各学院等）抓取最新的通知列表。
- **增量更新**：只抓取上次运行后发布的新通知，避免重复处理。
- **数据存储**：将抓取到的通知数据（标题、链接、发布日期）保存在 CSV 文件中 (`data/gwt_data.csv`)。
- **AI 分类与总结**：
    - 使用 Google Gemini API 对抓取到的通知进行智能分类（例如：教学管理、科研项目、会议活动等）。
    - 针对用户选择的特定通知，能够抓取其详细内容（标题、正文、附件）并生成内容摘要。
- **配置管理**：通过 `config.env` 文件管理必要的配置信息，如 `GEMINI_API_KEY` 和用户类型。
- **交互式配置**：如果 `config.env` 文件或其中的关键配置项缺失，程序会引导用户输入并自动保存。
- **格式化输出**：将 AI 处理后的通知信息以清晰、易读的格式展示出来。

## 项目结构

```
/Users/drc/Code/project/tsuko/
├── data/                     # 存放数据文件
│   └── gwt_data.csv          # 爬取的通知原始数据
│   └── response.txt          # AI处理后的响应（旧版，可能已弃用）
├── src/                      # 源代码目录
│   ├── main.py               # 主程序入口，协调各模块工作
│   ├── gwt.py                # 负责官网通知的抓取、数据处理和格式化输出
│   ├── ai_analyse.py         # 负责与 Google Gemini API 交互，进行内容分类和总结
│   └── __pycache__/          # Python 编译的缓存文件
├── test/                     # 测试代码目录
│   └── crawler.py            # 用于测试爬虫和AI分析功能的脚本
├── res/                      # 资源文件目录
│   └── prompt.txt            # AI 模型的提示语（prompt）
│   └── prompt/
│       └── classify.txt      # 分类任务的特定prompt
│       └── details_summary.txt # 详情总结任务的特定prompt
│       └── nyaa.txt          # 猫娘模式的通用prompt
├── config.env                # 配置文件 (需要用户自行创建或由程序引导创建)
└── README.md                 # 项目说明文件 (即本文档)
```

## 安装与运行

### 1. 环境准备

- Python 3.x
- pip (Python 包管理工具)

### 2. 安装依赖

在项目根目录下，运行以下命令安装必要的 Python 库：

```bash
pip install requests beautifulsoup4 pandas python-dotenv google-generativeai
```

### 3. 配置 API Key

项目需要使用 Google Gemini API。请按照以下步骤操作：

1.  获取您的 Google Gemini API Key。
2.  在项目根目录下创建（或等待程序引导创建）一个名为 `config.env` 的文件。
3.  在 `config.env` 文件中添加以下内容，并将 `你的API密钥` 替换为您的真实 API Key：
    ```env
    GEMINI_API_KEY=你的API密钥
    USER_TYPE=1 # 用户类型，例如 1 代表本科生，具体含义见代码或提示
    DAYS_TO_ANALYZE=2 # 分析最近几天的通知，默认为2
    ```
    如果文件或配置项不存在，首次运行 `src/main.py` 时，程序会提示您输入。

### 4. 运行主程序

```bash
python src/main.py
```

程序将开始抓取新通知，进行 AI 分析，并输出结果。

### 5. (可选) 运行测试脚本

可以运行 `test/crawler.py` 来单独测试爬虫或 AI 分析的特定功能。

```bash
python test/crawler.py
```

## 主要模块说明

-   **`src/main.py`**: 
    -   程序的主入口。
    -   负责初始化配置，调用 `gwt.py` 中的函数获取和存储通知数据，然后调用 `ai_analyse.py` 中的函数进行 AI 处理，最后格式化并输出结果。
-   **`src/gwt.py`**: 
    -   `get_data_from_gwt()`: 从官网爬取通知列表，进行增量更新，并将数据保存到 `gwt_data.csv`。
    -   `get_data_stored()`: 从 `gwt_data.csv` 读取指定日期范围内的通知数据。
    -   `get_page_details(url)`: 爬取指定 URL 页面的详细信息（标题、正文、附件）。
    -   `format_gwt_list()`: 将 AI 分类后的通知列表格式化为易读的文本。
-   **`src/ai_analyse.py`**: 
    -   `ai_classify(user_type, data)`: 调用 Gemini API 对输入的通知数据列表进行分类。
    -   `ai_details_summary(data)`: 调用 Gemini API 对单个通知的详细内容进行总结。
    -   `talk_with_mashiro()`: (实验性功能) 提供一个与 AI 聊天的交互界面，可以调用已定义的工具函数。

## 注意事项

-   请确保您的网络连接正常，以便访问深圳技术大学官网和 Google Gemini API。
-   API Key 的保密性非常重要，请勿泄露。
-   爬虫的效率和稳定性可能受目标网站结构变化的影响。如果抓取失败，可能需要更新 `gwt.py` 中的爬虫逻辑。
-   AI 的输出质量取决于 prompt 的设计和模型的性能。

## 未来展望

-   更精细化的通知分类。
-   支持更多学校或信息来源。
-   提供 Web 界面或桌面应用。
-   更智能的个性化通知推送。

---

