# HiChannel

Home Assistant custom integration，透過 `media-source://hichannel/<channel-id>` 播放線上廣播電台。

## 支援頻道

| Channel ID | 頻道名稱 |
|---|---|
| `bestradio` | Best Radio 好事聯播網 |

## 安裝

### 透過 HACS（建議）

1. 在 HACS 中新增 Custom Repository：
   - Repository：`https://github.com/nono-liang/hichannel`
   - Category：`Integration`
2. 搜尋 **HiChannel** 並安裝
3. 重啟 Home Assistant
4. 前往 **設定 → 整合 → 新增整合**，搜尋 **HiChannel** 並完成設定

### 手動安裝

1. 將 `custom_components/hichannel/` 複製到 HA 的 `config/custom_components/hichannel/`
2. 重啟 Home Assistant
3. 前往 **設定 → 整合 → 新增整合**，搜尋 **HiChannel** 並完成設定

## 使用方式

### 透過媒體瀏覽器

安裝後在媒體播放器的瀏覽器中會出現 **HiChannel** 分類，點選頻道即可播放。

### 透過 Service 呼叫

```yaml
service: media_player.play_media
target:
  entity_id: media_player.your_player
data:
  media_content_id: media-source://hichannel/bestradio
  media_content_type: music
```

### 透過 Dashboard 按鈕

```yaml
type: button
name: Best Radio
icon: mdi:radio
tap_action:
  action: call-service
  service: media_player.play_media
  service_data:
    entity_id: media_player.your_player
    media_content_id: media-source://hichannel/bestradio
    media_content_type: music
```

## 運作原理

播放時 integration 會即時向頻道來源網站發送請求，從頁面中解析 HLS（`.m3u8`）串流網址，再交由媒體播放器播放。因此需要 Home Assistant 能夠存取網際網路。

## 需求

- Home Assistant 2023.1.0 以上
- 支援 HLS 播放的媒體播放器（例如：Chromecast、VLC、MPD）

## 疑難排解

**播放失敗 / unknown_media_source**
- 確認已在 **設定 → 整合** 中新增 HiChannel
- 重新載入 integration 或重啟 HA

**串流無法解析**
- 頻道網站可能暫時無法存取，或頁面結構已更新
- 至 **設定 → 系統 → 記錄檔** 搜尋 `hichannel` 查看詳細錯誤

開啟 debug log：

```yaml
logger:
  logs:
    custom_components.hichannel: debug
```
