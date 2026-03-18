# chan-skills

Chan Openclaw skills for E-Commerce content creation (practical AI tools and skills).

中文版本见 [README.zh-CN.md](README.zh-CN.md)。

## Install

```bash
# List available Chan skills
npx skills add chanjing-ai/chan-skills --list

# Install all Chan skills
npx skills add chanjing-ai/chan-skills

# Install a specific skill
npx skills add chanjing-ai/chan-skills --skill chanjing-tts -y
```

## Symlink to .agents/skills (optional)

To keep this repo’s skills in sync with `~/.agents/skills` (or a custom directory):

```bash
# One-time: symlink each skill under skills/ to the target (new skills will need re-run)
SKILLS_LINK_TARGET=/Users/molo/Projects/skills/.agents/skills ./scripts/symlink-skills-to-agents.sh

# Optional: run the above after every git pull (install Git post-merge hook)
cp scripts/git-hooks/post-merge .git/hooks/post-merge && chmod +x .git/hooks/post-merge
```

Override the target with env `SKILLS_LINK_TARGET` (default: `/Users/molo/Projects/skills/.agents/skills`). The script is idempotent; new skills get linked when run again; broken links are removed.

## Get and set API keys (Chan Jing / 蝉镜)

Before using Chan Jing (蝉镜) skills (TTS, digital avatar, voice clone, etc.), configure **Access Key (app_id)** and **Secret Key (secret_key)**. See [chanjing-credentials-guard](skills/chanjing-credentials-guard/SKILL.md) for details.

### Get API keys

1. Open the Chan Jing sign-up/login page to obtain AK/SK:
   ```bash
   python skills/chanjing-credentials-guard/scripts/open_login_page
   ```
   Or open in a browser: <https://www.chanjing.cc/openapi/login>  
2. After signing up or logging in, create an API key in the console and copy **app_id** and **secret_key**.

### Set API keys

Run in your terminal (replace `<your_app_id>` and `<your_secret_key>` with your values):

```bash
python skills/chanjing-credentials-guard/scripts/chanjing-config --ak <your_app_id> --sk <your_secret_key>
```

Credentials are written to `~/.chanjing/credentials.json` (override the directory with env `CHANJING_CONFIG_DIR`). After setting, re-run your intended action.

Check current config status:

```bash
python skills/chanjing-credentials-guard/scripts/chanjing-config --status
```

## Available skills

| Name | Description |
|------|-------------|
| chanjing-credentials-guard | Credentials guard: validate AK/SK and Token before any Chanjing API; guide login and Shell config when missing. Run first before other Chanjing skills. |
| chanjing-tts | Bilingual text-to-speech using provided voices (Chinese and English). |
| chanjing-tts-voice-clone | Bilingual TTS using a user-provided reference voice. |
| chanjing-avatar | Lip-sync / digital avatar video generation. |
| chanjing-video-compose | Digital human video synthesis from text or audio, with task polling and optional local download. |
| chanjing-customised-person | Create, inspect, poll, and delete customised digital humans from uploaded source videos. |
| chanjing-text-to-digital-person | Create AI digital person images from prompts, turn them into short talking videos, and optionally run LoRA tasks. |
| chanjing-ai-creation | Generic AI creation task runner for supported image/video models, with submit, list, detail, polling, and download workflows. |
