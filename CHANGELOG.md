# Changelog

> 版本格式：`v0.<feature>.<patch>`

## v0.3.0 — 2026-05-03

### 改进：对比度优先的调色板算法

**问题：** KMeans 按像素频率分配颜色时，大面积主色会占掉多个颜色槽，导致眼睛、眉毛等占比小但高对比度的颜色被牺牲。

**方案：** KMeans ×2 → 去重合并
1. 先跑 KMeans 生成 2 倍候选色（如 6 色目标 → 12 候选）
2. 贪心合并最近似的颜色对（欧式距离 < 30 视为冗余）
3. 确保调色板无浪费的近似色，释放给高对比色

**涉及文件：**
- `backend/app/processors/quantize.py` — 新增 `_deduplicate()`，修改 `extract_colors()`

**效果：** 梯度图平均色距从 162 提升至 191（+18%）

---

## v0.2.0 — 2026-05-03

### 新增：边缘保留像素化（结构线覆盖）

**问题：** 像素数量少时，LANCZOS 下采样会平均掉眼睛、眉毛、嘴等细小但关键的结构。

**方案：** Sobel 边缘检测 → 下采样到网格 → 结构线遮罩 → 颜色加深
1. 在原图分辨率上计算 Sobel 梯度边缘图
2. 下采样边缘图到目标网格，取 top 20% 格子作为结构线遮罩
3. 对这些格子做颜色加深（乘 `1 - strength`），突出结构线

**涉及文件：**
- `backend/app/processors/edge_preserve.py` — 新建，含 `compute_edge_map()` / `downscale_edge_map()` / `generate_outline_mask()` / `darken_outline()`
- `backend/app/main.py` — `_process_image()` 集成边缘流水线
- `backend/app/schemas.py` — 新增 edge_preserve / edge_strength 参数
- `frontend/src/types.ts` — 前端 Params 类型扩展
- `frontend/src/api.ts` — 请求参数扩展
- `frontend/src/components/ParameterPanel.tsx` — 新增结构线开关 + 强度滑块
- `frontend/src/App.tsx` — 默认参数更新

**效果：** 22×27 网格中，眼、眉、鼻、嘴、脸型轮廓的结构线遮罩位置正确。

---

## v0.1.2 — 2026-05-03

### 修复：像素数量输入框无法清空重输

**问题：** `<input type="number">` 的 onChange 里用 `Math.max(16, ...)` 拦截了空值，导致删光数字后自动弹回 16。

**方案：** 改用独立 `pixelInput` 字符串状态，允许空输入，失焦（onBlur）时 clamp 到 16~10000。

**涉及文件：**
- `frontend/src/components/ParameterPanel.tsx` — 新增 `useState` + `onBlur` 逻辑

---

## v0.1.1 — 2026-05-03

### 修复：竖拍图片被横置处理

**问题：** 手机/相机拍的竖图在像素数据中是横着的，PIL 默认不读取 EXIF 方向标记。

**方案：** 在 `_load_image()` 中用 `ImageOps.exif_transpose()` 自动旋转。

**涉及文件：**
- `backend/app/main.py` — 新增 `_load_image()` 统一加载入口

---

## v0.1.0 — 2026-05-03

### 项目初始化

前后端分离架构搭建，完成图片转像素图核心流程。

**功能：**
- 后端 FastAPI，3 个端点：`/api/convert`、`/api/preview`、`/api/export`
- 前端 React + Vite + TypeScript，单页布局：上传 → 参数 → 预览 → 导出
- 像素网格尺寸自动分配（保持比例，总像素 ≈ 输入值）
- 三种颜色模式：单色（1 色）、均衡（默认 6 色，可调）、写实（默认 20 色，可调）
- 预处理：中值滤波去噪（强度可调）
- 导出：PNG 网格图 / PDF（含色号标注）
- Vite 代理 `/api` → 后端 8000，前端仅需访问 5173

**涉及文件：**
- `backend/requirements.txt`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/__init__.py`
- `backend/app/processors/__init__.py`
- `backend/app/processors/pixelate.py` — 网格计算 + 像素化
- `backend/app/processors/quantize.py` — KMeans 颜色量化
- `backend/app/preprocess/__init__.py`
- `backend/app/preprocess/denoise.py` — 中值滤波去噪
- `backend/app/exporters/__init__.py`
- `backend/app/exporters/png_exporter.py` — PNG 网格导出
- `backend/app/exporters/pdf_exporter.py` — PDF 导出（reportlab）
- `frontend/` — Vite + React + TypeScript 项目
- `frontend/src/App.tsx` — 主页面
- `frontend/src/App.css` — 样式
- `frontend/src/index.css` — 全局样式
- `frontend/src/types.ts` — 类型定义
- `frontend/src/api.ts` — API 客户端
- `frontend/src/components/ImageUploader.tsx`
- `frontend/src/components/ParameterPanel.tsx`
- `frontend/src/components/PreviewPanel.tsx`
- `frontend/vite.config.ts` — 代理配置
- `frontend/package.json` — concurrently 脚本
- `README.md` — 项目文档
