# chan-skills

面向电商内容创作的 Chan Openclaw 技能集合（实用 AI 工具与技能）。

English version: [README.md](README.md)

## 安装

```bash
# 列出可用的 Chan 技能
npx skills add chanjing-ai/chan-skills --list

# 安装全部 Chan 技能
npx skills add chanjing-ai/chan-skills

# 安装指定技能
npx skills add chanjing-ai/chan-skills --skill chanjing-tts -y
```

## 链接到 `.agents/skills`（可选）

如果你希望这个仓库里的技能与 `~/.agents/skills`（或自定义目录）保持同步：

```bash
# 一次性：将 skills/ 下的每个技能软链接到目标目录（新增技能后需要重新执行）
SKILLS_LINK_TARGET=/Users/molo/Projects/skills/.agents/skills ./scripts/symlink-skills-to-agents.sh

# 可选：每次 git pull 后自动执行上面的逻辑（安装 Git post-merge hook）
cp scripts/git-hooks/post-merge .git/hooks/post-merge && chmod +x .git/hooks/post-merge
```

可通过环境变量 `SKILLS_LINK_TARGET` 覆盖目标目录（默认值：`/Users/molo/Projects/skills/.agents/skills`）。该脚本支持重复执行；重新运行后会为新增技能创建链接，并移除失效链接。

## 获取并设置 API Key（Chan Jing / 蝉镜）

在使用 Chan Jing（蝉镜）相关技能（TTS、数字人、声音复刻等）之前，需要先配置 **Access Key (`app_id`)** 和 **Secret Key (`secret_key`)**。详细说明见 [chanjing-credentials-guard](skills/chanjing-credentials-guard/SKILL.md)。

### 获取 API Key

1. 打开蝉镜注册/登录页面以获取 AK/SK：
   ```bash
   python skills/chanjing-credentials-guard/scripts/open_login_page.py
   ```
   或直接在浏览器中打开：<https://www.chanjing.cc/openapi/login>  
2. 注册或登录后，在控制台创建 API Key，并复制 **app_id** 和 **secret_key**。

### 设置 API Key

在终端中运行以下命令（将 `<your_app_id>` 和 `<your_secret_key>` 替换为你的实际值）：

```bash
python skills/chanjing-credentials-guard/scripts/chanjing_config.py --ak <your_app_id> --sk <your_secret_key>
```

凭据会写入 `~/.chanjing/credentials.json`（也可通过环境变量 `CHANJING_CONFIG_DIR` 覆盖目录）。设置完成后，重新执行你原本要运行的操作即可。

查看当前配置状态：

```bash
python skills/chanjing-credentials-guard/scripts/chanjing_config.py --status
```

## 可用技能

| 名称 | 说明 |
|------|------|
| chanjing-credentials-guard | 凭据守卫：在调用任何蝉镜 API 前校验 AK/SK 和 Token；缺失时引导登录和 Shell 配置。建议在其他蝉镜技能之前先运行。 |
| chanjing-tts | 使用内置音色进行中英文文本转语音。 |
| chanjing-tts-voice-clone | 使用用户提供的参考音色进行中英文 TTS。 |
| chanjing-avatar | 唇形驱动 / 数字人视频生成。 |
| chanjing-video-compose | 基于文本或音频合成数字人视频，支持任务轮询和可选本地下载。 |
| chanjing-customised-person | 基于上传源视频创建、查看、轮询和删除定制数字人。 |
| chanjing-text-to-digital-person | 通过提示词创建 AI 数字人形象，将其转成短口播视频，并可选执行 LoRA 任务。 |
| chanjing-ai-creation | 蝉镜 AI 创作 Open API 客户端：提交任务、轮询状态、列表/查询任务、可选下载；读写本地 credentials.json。 |
| chanjing-one-click-video-creation | 选题或工作流一键短视频成片：文案、分镜、TTS、数字人合成、AI 画面与本地封装；编排蝉镜 Open API 与同仓库子技能；需 **ffmpeg** / **ffprobe**。 |
