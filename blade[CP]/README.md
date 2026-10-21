# 刃（HSR） - Stardew Valley Content Patcher NPC

这是一个适用于星露谷物语 1.6 / Content Patcher 的自定义 NPC 内容包。当前配置目标：

- 可攻略、可结婚
- 有日常对话、生日对话、节日对话、婚后对话
- 有礼物喜好与每周日程
- 支持姜岛度假村

## 当前进度

### 1. 行走图（已生成四季版本）

已根据 `asset/_source/walk_template.psd` 生成四张 64×128 行走图：

- `asset/sprites/blade_spring.png`
- `asset/sprites/blade_summer.png`
- `asset/sprites/blade_fall.png`
- `asset/sprites/blade_winter.png`

`content.json` 已通过 `{{Season}}` 自动按季节加载。每张图都是 4 列 × 4 行，单帧 16×32；第四行由右侧行走帧镜像补成左侧行走。

### 2. 头像（临时草稿已生成）

为了先跑通游戏，已生成一张临时头像表：

- `asset/portrait/blade.png`：头像表

- 头像：单格 64×64；常用格式为 2 列 × 6 行，共 128×384。
- PNG 透明背景，不要缩放。

这张草稿是用冬季行走图的头部放大的，12 个表情槽暂时使用同一张脸。正式头像画完后直接覆盖这个文件即可；如果要做四季头像，再告诉我，我会改成按季节切换。

### 2.2 实机加载测试

已在 `Stardew Valley 1.6.15` + `SMAPI 4.5.2` + `Content Patcher 2.9.1` 下启动测试：

- 内容包「刃」成功加载
- `Data/Characters` 成功写入
- `Data/NPCGiftTastes` 成功写入
- SMAPI 未报告 Content Patcher 加载错误

出生点使用 `FarmHouse 27,25`。升级农舍 `FarmHouse2` 的门位于 `27,31`。

### 2.1 尚未完成或尚未验证的内容

- 自定义住房、房屋外观和室内布局：尚未制作
- 配偶房间、农场庭院：尚未制作
- 好感事件、剧情任务、电影反应：尚未添加
- 当前日程坐标来自参考 NPC 包，尚未在你的完整 mod 组合中实测
- 出生点暂时放在玩家农场小屋 `FarmHouse 27,25`

### 3. 已采用的设定

- 角色的正式中文名与英文内部 ID（当前为「刃」/`blade`）
- 性别、年龄：成年男性
- 生日：春季 9 日（对应 5 月 9 日）
- 性格：寡言、克制、带旧伤和沉重感，恋爱线逐渐松动
- 住处（当前临时为玩家农场小屋 `FarmHouse 27,25`）
- 日程：8:00 出门，16:00 回农舍；雨天全天在屋内走动

### 5. 行为扩展（需要额外安装）

`companion/BladeBehaviors` 是独立 SMAPI 模组，用于补足 Content Patcher 无法完成的行为：

- 雨天在农舍和刃互动时，消耗冰箱里最多 2 份食材并给玩家一份料理
- 好感达到 8 心后，每周第一次互动赠送一份红宝石
- 保留 `CanGreetNearbyCharacters`，让刃能和其他 NPC 打招呼；靠近其他 NPC 时会偶尔显示短句气泡

已安装为 `Mods\[SMAPI] Blade Behaviors`，它会自动要求 Content Patcher。原版不支持 NPC 之间的完整剧情对话，当前实现的是短句问候气泡。

### 6. 节日与农舍巡游

- 已加入花舞节专用行走图 `blade_flowerdance.png`（64×160，前 4 行沿用常规行走图，第 5 行为舞蹈帧）
- 已加入 8 个节日的 NPC 站位数据
- 16:00 后农舍巡游改为每 20 分钟切换安全空地
- 行为模组会关闭 `willDestroyObjectsUnderfoot`，避免刃踩坏家具
- 如果在农舍内持续卡住 15 秒，会自动回到安全点 `FarmHouse 27,25`

注意：花舞节舞蹈帧目前是从 PSD 模板组换色得到的占位版本，人物发型仍接近模板；婚礼/亲吻组也还是模板角色，尚未接入正式动画。
- 礼物：偏好矿石、宝石、金属锭和辛辣食物
- 对白：保留当前草稿风格

### 4. 婚后内容（可选但建议）

当前没有自定义配偶房间和农场庭院，结婚后会使用默认房间。要完善需要：

- 配偶房间地图（6×9 格左右）
- 农场庭院地图（可选，最多 4×4 格）

## 安装测试

把整个 `blade[CP]` 文件夹放进：

```text
Stardew Valley/Mods/
```

通过 SMAPI 启动游戏。当前行走图和临时头像都已存在，可以直接测试加载。

## 兼容性

本包只使用 Content Patcher 的数据和图片编辑，没有 C# 代码或 Harmony 补丁，通常可以与大多数 mod 共存。需要注意：

- 其他 NPC mod 如果也使用内部 ID `blade` 或 UniqueID `tr.blade`，会发生冲突。
- 改变 Town 地图的 mod（例如大型地图扩展）可能让日程坐标失效。
- 其他 NPC 的日程如果占用同一批坐标，可能出现角色重叠，但通常不会崩溃。
- `Data/Festivals/spring24` 的 `FlowerDance_Accept` / `FlowerDance_Decline` 是全局键，其他 mod 若也修改这些键，会由加载顺序决定最终文本。

## 工作文件

以下内容只用于制作，发布或打包 mod 时建议排除：

- `asset/_source/`：PSD 原件、预览图和生成脚本输出
- `tools/make_seasonal_sprites.py`：四季行走图生成脚本
- `.venv/`：本地 PSD 解析环境
