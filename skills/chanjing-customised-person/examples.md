# Examples

## Natural Language Triggers

这些说法通常应该触发本 skill：

* “帮我把这段视频训练成蝉镜定制数字人”
* “上传这个 mp4 创建一个新的数字人形象”
* “查一下我现有的定制数字人列表”
* “帮我轮询这个定制数字人的状态”
* “把这个定制数字人删掉”

## Minimal CLI Flows

### 1. 上传并创建

```bash
FILE_ID=$(python3 skills/chanjing-customised-person/scripts/upload_file.py \
  --file ./source.mp4)

PERSON_ID=$(python3 skills/chanjing-customised-person/scripts/create_person.py \
  --name "产品演示数字人" \
  --file-id "$FILE_ID" \
  --train-type figure)

python3 skills/chanjing-customised-person/scripts/poll_person.py --id "$PERSON_ID"
```

### 2. 获取完整详情

```bash
python3 skills/chanjing-customised-person/scripts/get_person.py \
  --id "C-ef91f3a6db3144ffb5d6c581ff13c7ec"
```

### 3. 只拿某个字段

```bash
python3 skills/chanjing-customised-person/scripts/get_person.py \
  --id "C-ef91f3a6db3144ffb5d6c581ff13c7ec" \
  --field audio_man_id
```

### 4. 列表查看

```bash
python3 skills/chanjing-customised-person/scripts/list_persons.py
```

### 5. 删除

```bash
python3 skills/chanjing-customised-person/scripts/delete_person.py \
  --id "C-ef91f3a6db3144ffb5d6c581ff13c7ec"
```

## Expected Outputs

* `upload_file.py` 输出 `file_id`
* `create_person.py` 输出 `person_id`
* `poll_person.py` 默认输出 `preview_url`
* `get_person.py` 默认输出详情 JSON
* `delete_person.py` 输出被删除的 `person_id`
