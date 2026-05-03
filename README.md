# img2pixel

将任意图片转换为**拼豆（Perler Beads / Fuse Beads）用像素图**。保留原图感觉，输出网格化像素图，支持色号标注与导出。

## 功能

- **图片上传** — 拖拽或点击上传任意图片，即时预览原始图和转换效果
- **像素数量控制** — 输入目标像素总数（如 600），系统根据图片宽高比自动分配为合理尺寸（10×60 / 20×30 等），上下波动以凑成整数
- **三种颜色模式**
  - **单色** — 整张图提炼为一种颜色（最接近图片主色调）
  - **均衡** (默认) — 用最少的颜色呈现，默认最多 6 色，减少拼豆材料种类，用户可自定义最大颜色数
  - **写实** — 尽可能保留原始色彩信息，默认最多 20 色，用户可自定义最大颜色数
- **预处理** — 自动去除背景噪点（可选手动调整阈值/强度）
- **导出** — 导出为 PNG 网格图或 PDF，标注色号/颜色编号，方便按图拼豆
- **参数可调** — 前端面板实时调整全部参数，所见即所得

## 技术栈

```
frontend/            React + Vite + TypeScript
backend/             Python FastAPI + Pillow / OpenCV
```

## 项目结构

```
img2pixel/
├── frontend/          # React 前端 (Vite)
│   ├── src/
│   │   ├── components/    # 上传区、参数面板、预览区
│   │   ├── api/           # 后端 API 调用
│   │   └── App.tsx
│   └── package.json
├── backend/           # Python 后端 (FastAPI)
│   ├── app/
│   │   ├── main.py        # 入口 & 路由
│   │   ├── processors/    # 像素转换逻辑
│   │   │   ├── quantize.py    # 颜色量化
│   │   │   └── pixelate.py    # 像素化处理
│   │   ├── preprocess/    # 预处理（去噪等）
│   │   └── exporters/     # 导出（PNG/PDF）
│   └── requirements.txt
└── README.md
```

## 快速开始

### 1. 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

后端运行在 `http://localhost:8000`，API 文档自动生成于 `/docs`。

### 2. 前端（另一个终端）

```bash
cd frontend
npm install
npm run dev
```

前端运行在 `http://localhost:5173`，API 请求自动代理到后端，只需访问这一个地址。

## API 概览

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/convert` | POST | 上传图片 + 参数，返回转换结果 |
| `/api/preview` | POST | 上传图片，返回预处理后的预览 |
| `/api/export` | POST | 导出为 PNG / PDF |
| `/api/health` | GET | 健康检查 |

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `pixel_count` | int | 600 | 目标像素总数 |
| `color_mode` | string | `balanced` | `monochrome` / `balanced` / `realistic` |
| `max_colors` | int | — | 均衡默认 6，写实默认 20，单色忽略 |
| `denoise` | bool | true | 是否自动去噪 |
| `denoise_strength` | float | 0.5 | 去噪强度 (0~1) |

## 开发计划

- [x] 需求整理
- [ ] 后端核心：像素化 + 颜色量化
- [ ] 后端预处理：去噪接口
- [ ] 后端导出：PNG / PDF
- [ ] 前端基础：上传 + 参数面板 + 预览
- [ ] 前后端联调
- [ ] 导出功能前端集成
