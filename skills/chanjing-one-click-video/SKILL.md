---
name: chanjing-one-click-video
description: 用户输入一个选题，自动生成完整短视频成片（文案、分镜、数字人口播 + AI 画面混剪）。适用于「一键成片」「根据选题做视频」等场景。
---

# chanjing-one-click-video

## 速查

| 内容 | 位置 |
|------|------|
| 工作流、`duration_sec`、`null`/合并、选题校验 | **§4.1** |
| 切段、奇偶镜、`scenes[]`、`scene_count`/`video_type` | **`storyboard_prompt.md`** 篇首；**`video_brief_plan.md`** |
| 渲染技术、状态、`partial`/success、硬约束 | **`render_rules.md`** §1–§4；**§7**、**§8** |
| **`ref_prompt` / 文生提示词** | **`storyboard_prompt.md`** + **`history_storyboard_prompt.md`**；**§4.2** 指针 |
| 请求体字段与默认 | **§6** |
| `run_render.py` | **§5** |

**冲突**：渲染实现以 **`render_rules.md`** 为准；**`ref_prompt`** 条文以 **`storyboard_prompt.md`** / **`history_storyboard_prompt.md`** 为准（**§4.2** 汇总指针）。`run_render.py` 只实现 **§5** + **`render_rules.md`**，不增业务规则。执行：手工编排子 skill、仅 `run_render`、或混用。

---

## 1. 做什么

1. 选题或全文 → `video_plan`、口播全文、分镜  
2. **TTS**：整段优先；超长按分镜少批合并（细则与字数见 **`render_rules.md` §3·C.4**）  
3. 按镜切音频  
4. **数字人分镜**：`chanjing-video-compose`（音频驱动）  
5. **AI 分镜**：`ref_prompt` → `chanjing-ai-creation` → 与镜内音频合成  
6. **封装**：对齐公共数字人轨 → **ffmpeg** concat → 本地 mp4  

---

## 2. 何时用 / 何时不用

| | |
|--|--|
| **适合** | 要成片；口播与画面混剪；用户明确要生成短视频 |
| **不适合** | 仅文案/标题；未要视频；只剪已有素材 |

---

## 3. 前置条件

- **鉴权**：`chanjing-credentials-guard`；`~/.chanjing/credentials.json`；无凭证时子进程可 `open_login_page`  
- **Plan/Script/分镜**：本地 Agent 逻辑，**无需**外部 LLM API key（本 skill 必选路径不依赖外部 LLM）  
- **本机**：`ffmpeg`、`ffprobe`  
- **`run_render` / 仓库根**：未设置 **`CHAN_SKILLS_DIR`** 时，脚本按自身路径推断：自 `skills/chanjing-one-click-video/scripts/run_render.py` **向上四级**为含 `skills/chanjing-tts` 等的仓库根。仅当目录布局不是「仓库内标准 skill 路径」或单独拷贝本 skill 时，才需显式设置 **`CHAN_SKILLS_DIR`**  
- **数字人与音色**：**勿**用环境变量或仓库内缓存文件保存跨任务的「默认」`audio_man` / `person_id` / `figure_type`。每次任务在 **`workflow.json` 根级显式填写**；由 Agent 按 **`video_plan`**（如 `video_type`）、口播人设与选题语义，调用 **`list_voices`** 与 **`list_figures`**（`--source` 取 `common` / `customised` 等与本次任务一致）选型后写入；**`audio_man`** 宜与所选形象的 **`audio_man_id`** 一致。
- **公共数字人选型（禁止「只取列表前几项」）**：须用 `list_figures --source common --json` 拉取候选（必要时增大 `--page-size` 或翻页，覆盖足够条目），在候选内**逐项对比**后再定稿：`name`、`figures[].type`（→ `figure_type`）、`figures[].width`/`height`（画幅与 **D.1c** 一致）、`audio_man_id`、`audio_name`（若有）与 **`video_plan`/口播人设**（性别、气质、行业、年龄感）是否匹配。**默认偏好年轻、有活力的形象**：名称或 `audio_name` 中含青年/少女/小哥哥/小姐姐/学生/元气/青春/年轻等正向信号时优先；仅当选题或用户明确要求成熟、权威、中老年等气质时，再选对应人设。定制源 `customised` 同样对比 `name`、`width`/`height`、`audio_man_id` 等，勿未经比较直接取页首。

---

## 4. 规则汇编

### 4.1 工作流编排

**合并**：`null` = 不覆盖。顺序：默认铺底 → 非 `null` 覆盖 → 布尔/整数校正。字段默认见 **§6**；未在表中展开的缺省由 **`run_render.py`**（及子进程）按实现与环境变量读取（**不含**音色/数字人：`audio_man`、`person_id`/`avatar_id`、`figure_type` 仅来自 **`workflow.json`**，见 **§3**）。

**`duration_sec`**：策划参考，非 ffmpeg 上限。**成片时长**以 TTS+`ffprobe` 为准。`scene_count` 见 **`video_brief_plan.md`**；切段与 AI 条数依实测与字幕轴（**`render_rules.md` §3·C.5**）。禁止为凑时长裁已定稿口播（除非用户要求）。

**选题**：去空白 <5 字、占位串（如「你好」「test」）拒收；可扩写；严格模式模糊则失败。

**步骤**：1) Plan → `video_brief_plan`（败则全败；模板见 **`video_brief_plan.md`**）2) Script 3) Storyboard：语义切分；**`storyboard_prompt.md`**；非当代 **`history_storyboard_prompt.md`**；DH **`chanjing-video-compose`**，AI **`chanjing-ai-creation`**；TTS/多段 AI/mux **`render_rules.md` §3**、**§5** 4) Render：**`render_rules.md` §3**（含 **§3·C.6**）、**§4**（表 4–6）；`ref_prompt` 质检见 **`storyboard_prompt.md`** / **`history_storyboard_prompt.md`**（**§4.2**）；重试/`partial` **`render_rules.md` §1** 5) 成功：**`render_rules.md` §1**  

**仅渲染**：`run_render.py` + `full_script` + `scenes[]`。**顺序**：Plan → Script → Storyboard → Render（各阶段用哪份模板见上列步骤）。

---

### 4.2 文生视频提示词（`ref_prompt`）— 指针

**唯一条文真值**（修订以模板为准，本文不重复 D.1–D.4 表文）：

| 范围 | 模板 |
|------|------|
| 当代向、**D.0** 语境缺省与文明圈推断、D.1 长度、**D.1a**、**D.1b**（易幻觉，全 skill 共用）、D.2 当代、手工 `visual_prompt`、D.3、D.4 当代装配与 7 要素 / 题材簇 / 单镜拼装 / 自检 | **`templates/storyboard_prompt.md`** → **「文生视频提示词（当代向真值）」** |
| **D.2 非当代**路由、历史**流程层**、**文明圈与国别自洽**、占位符纪律、与 D.3/D.4 衔接说明 | **`templates/history_storyboard_prompt.md`** |
| 族裔、**历史/非当代中式造型**与出现人物时的英文短语 | **`templates/visual_prompt_people_constraint.md`**（显式族裔锚定、**历史 / 非当代**节；兼 **`render_rules.md` §4** 表 4–6） |

**仍仅在此处索引**：长音频多段 **`render_rules.md` §3·C.6**；字数上限环境变量 **`AI_VIDEO_PROMPT_MAX_CHARS`**。模板与 **`render_rules.md`** 实现冲突时以 **`render_rules.md`** 为准。

---

## 5. 自动化编排（`run_render.py`）

**依赖**：鉴权；`CHAN_SKILLS_DIR`（§3）；`chanjing-tts` / `chanjing-video-compose` / `chanjing-ai-creation`

**职责**：① TTS+`audio_task_state`；批合并与单批字数上限见 **`render_rules.md` §3·C.4**（`TTS_BATCH_MAX`）② 切段（**`render_rules.md` §3·C.5**）③ **有 AI 镜时先完成首条数字人并 `ffprobe`（含 `rotate`）→ 再按映射提交文生 `aspect_ratio`/`clarity`**（见 **`render_rules.md` §3·C.6**、`debug.ai_video_submit_params`）④ 与其余 DH/AI 并行 poll ⑤ AI 轨对齐该参照 `ffprobe` ⑥ ffmpeg concat ⑦ 多段文生在 `ref_prompt` 后追加英文分层；总长 `AI_VIDEO_PROMPT_MAX_CHARS`

**不做**：不产 plan/script/storyboard；不自动非当代/当代；不用 `list_tasks` 当代次（**`render_rules.md` §4 表项 8**）

**手工编排**：仍须满足 **`render_rules.md` §3、§4** 与 §5；§3 细化（如 `silencedetect`、`minterpolate`、参照轨码率、同套切段音频换形象、TTS 批间静音等）**全部保留**。

**输入 MVP**

| 字段 | 必填 | 说明 |
|------|------|------|
| `full_script` | 是 | 与各镜 `voiceover` 按 `scene_id` 拼，`norm` 一致 |
| `scenes` | 是 | `scene_id`、`voiceover`、`use_avatar`；AI 镜 `ref_prompt`（**`storyboard_prompt.md`** / **`history_storyboard_prompt.md`**；§4.2）；可选 `subtitle` |
| `audio_man` | 是 | 宜与所选数字人形象的 `audio_man_id` 一致 |
| `person_id`/`avatar_id` | 条件 | 有 DH 镜必填 |
| `figure_type` | 否 | 与当次 `list_figures` 所选形象行的 `figure_type` 一致（公共多形态时必填） |
| `subtitle_required` | 否 | 默认 false；为 true 时数字人镜烧录字幕（`--subtitle show`） |
| `speed`/`pitch` | 否 | 默认 1/1 |
| `ai_video_duration_sec` | 否 | 5 或 10，默认 10 |
| `model_code` | 否 | 默认 `AI_VIDEO_MODEL` 或 `Doubao-Seedance-1.0-pro`；creation_type=4；不传 `ref_img_url` |
| `max_retry_per_step` | 否 | 默认 1（§6） |

```bash
python scripts/run_render.py --input workflow.json --output-dir ./outputs/run1
```

**输出**：`final_one_click.mp4`；`workflow_result.json`；`work/`  

---

## 6. 输入（请求体）

**norm**：去 `\r`、首尾空白；空→空串；与 **`run_render.py`** 一致。口播：先 `full_script`，再 `script`→`copy_text`→`input_script`→`content` 首个非空。无 `topic`：首句代选题（40 字内遇句末标点截，否则 24 字）。`null`/合并 **§4.1**。

| 字段 | 必填 | 说明 |
|------|------|------|
| `topic` | 条件 | 无则见首句规则；建议 ≥5 字 |
| `industry`/`platform`/`style` | 否 | `industry` 空；platform/style：`DEFAULT_*` 或 `douyin`/`观点型口播` |
| `duration_sec` | 否 | `DEFAULT_DURATION` 或 60；策划参考 |
| `use_avatar` | 否 | 默认 true |
| `avatar_id`/`voice_id` | 否 | 空；**不得**用环境变量兜底音色或数字人；须在 `workflow.json` 写明 `audio_man`/`person_id`（及有 DH 镜时的 `figure_type`），由 Agent 按当次任务调用 `list_voices` 与 `list_figures`（来源与 **`video_plan`** / 用户指定一致）**对比 `name`、形态、画幅、`audio_name` 等后**选型；**禁止**未比较即取列表最前几条；**默认偏好年轻数字人**（见 **§3**） |
| `subtitle_required` | 否 | 默认 false（数字人成片不烧录字幕；`run_render` 传 `hide`） |
| `cover_required` | 否 | 默认 true |
| `strict_validation`/`allow_auto_expand_topic`/`max_retry_per_step` | 否 | true/false/1 |
| `full_script` | 否 | 默认空 |
| `script_title`/`script_hook`/`script_cta` | 否 | 默认空 |
| `script`/… | 否 | 见上文口播顺序 |

---

## 7. 输出 JSON

| 键 | 含义 |
|----|------|
| `status` | success / partial / failed |
| `video_plan` | Plan |
| `script_result` | title、hook、full_script、cta |
| `storyboard_result.scenes[]` | scene_id、duration_sec、voiceover、subtitle、visual_prompt、use_avatar |
| `render_result` | video_file、scene_video_urls、render_path、degrade_log |
| 其它 | error、debug… |

**渲染无降级**：任一步失败即中断，不自动改为仅 DH 或仅 AI 成片。**partial**：未成 success（如 `run_render` 异常仍写 `workflow_result.json`）；**不**表示允许上述降级，**不**免 **`storyboard_prompt.md`·D.1b** 类质检。成功 `degrade_log`=`[]`；失败尽量保留已产出文案与分镜。

---

## 8. 硬性约束

表在 **`templates/render_rules.md` §4**；与 `ref_prompt` 交叉见 **`storyboard_prompt.md`** / **`history_storyboard_prompt.md`**（**§4.2** 指针）。本节为锚点。

---

## 9. 限制

- 本地 mp4；不上传  
- AI 单段常 5–10s；长口播多段  
- 成片时长=TTS 总轨；可与 `duration_sec` 不符  
- **TTS**：整轨优先、超长少批合并；单批上限与合并策略（含 `TTS_BATCH_MAX`）以 **`render_rules.md` §3·C.4** 为准  
- 文生失败可能为平台/模型；试增 `max_retry_per_step`、短 `ref_prompt`、拆镜；查 `workflow_result.json`  

