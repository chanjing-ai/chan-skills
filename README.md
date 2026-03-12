# chan-skills

Chan Openclaw skills for E-Commerce content creation (practical AI tools and skills).

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

## Available skills

| Name | Description |
|------|-------------|
| chanjing-credentials-guard | Credentials guard: validate AK/SK and Token before any Chanjing API; guide login and Shell config when missing. Run first before other Chanjing skills. |
| chanjing-tts | Bilingual text-to-speech using provided voices (Chinese and English). |
| chanjing-tts-voice-clone | Bilingual TTS using a user-provided reference voice. |
| chanjing-avatar | Lip-sync / digital avatar video generation. |
