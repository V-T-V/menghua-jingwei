# 梦华经纬 · 东京梦华录数字人文站

> 宋·孟元老《东京梦华录》十卷——门谱、河道、街市、岁时四层织一座北宋东京（汴京）。
> 「经纬」系列第八站；与伽蓝经纬（北魏洛阳）构成**双京对照**。

## 一册书 · 一座城

《东京梦华录》成书于绍兴丁卯（1147），追记崇宁—宣和间汴京的城郭、河梁、
市肆、节物——孟元老自序所谓「華胥之夢」。本站以**城**为空间范式：

| 层 | 内容 | 数量（脚本口径） |
|---|---|---|
| 城防（卷一） | 外城/旧城/大内门谱 · 穿城四河 | 门 34（外16·舊12·大内6）· 河 4 · 桥 32 |
| 街市（卷二至五） | 州桥夜市 · 界身 · 瓦子 · 酒楼 · 相国寺… | 地条目 21 |
| 岁时（卷六至十） | 元宵 · 金明池争标 · 七夕 · 中秋 · 除夕… | 节序 43 |
| 语料 | 提要+自序+十卷 | 88 块 · 27,423 字 |

## 快速开始

```bash
python -m http.server 9900        # 起本地服务
python tools/fetch_text.py        # 抓语料（断点续抓，已缓存跳过）
python tools/parse_entries.py     # 解析 88 块（与抓取报告对账）
python tools/stats.py             # 计量 → docs/stats.json（唯一数字源）
python tools/build_data.py        # 构建 → site_data/sections/text（书证逐段验真）
python tools/lint.py              # 确定性检查
python run_tests.py               # 全套回归（v2）
```

## 功能

- **舆图**：自绘汴京示意平面（Leaflet L.CRS.Simple）——三层城垣、御街轴线、
  穿城四河线层、金明池水面、城门符号（按墙分级）、街市点（按类着色，径=条目字数）；
  左下**分层开关**（城垣/城门/河道/街市），点击门/河/市出书证卡片。
- **循读**：卷〇至卷十按节滚动读原文，舆图随文飞行；`#m=read#juan=N#jie=名` 深链写回。
- **岁时记**：卷六至十 43 节按农历月编年（正月灯山 → 除夕大傩），点击入循读。
- **检索**：全书懒加载扫描（27KB 整载），命中名物直落循读。
- **计量**：篇幅三层结构 / 分卷字数 / 岁时月分布 / 市井词频 / 门河提及。
- **双桥**（P2）：寰宇桥（↗太平寰宇記開封府对照）· 双京桥（↗伽蓝经纬北魏洛阳城制对读）。
- PWA 离线（SW 两级缓存）· 夜读 · TTS 听书 · 书签 · 名录导出 CSV(BOM)/KML/GeoJSON。

## 数据纪律（宁缺毋假）

- **文本**：kanripo **KR2k0111**（文淵閣四庫全書本 WYG，mandoku org 格式）via
  GitHub raw（断点续抓+限速+UA 自报家门，原始页留档 `data_raw/` 不入 git）。
  全书 88 节完整，无缺卷。**版本性质**：四库本异文/讳改不在校勘范围，依样保留
  （如卷一州橋夹注「正名**大**漢橋」，通行本作天漢橋）；kanripo 缺字实体 38 处以
  □ 代，`data_raw/` 可复核。繁体原样展示，界面用简体。
- **凡数字出自脚本**：docs/stats.json 是唯一数字源（tools/stats.py），前端/论文/README 只读。
- **坐标**：全部 `src:"derived"`——示意城市平面（米制，原点=外城西南角，x 东 y 北），
  外城 8,800×4,800m（「方圓四十餘里」量级，1 宋里≈560m），旧城 3,600×2,900（「方圓約二十里許」），
  大内 1,400×1,150。门/街市布点=卷一城防谱+卷二以下方位句+宋东京城考古常识量级；
  导出（CSV/KML/GeoJSON）逐行注明 src:derived，经纬为示意平面锚定 WGS84（量级推算，非实测）。
- **书证验真**：build_data.py 对每个门/河/街市/节序的引文片段逐段在语料中机械验证，
  验不中即构建失败（本站把「引用可复核」做进管线）。

## 测试与验证

- `python run_tests.py`：lint（598 项）+ 数据断言 + SHA256SUMS 对账（P2 起）。
- 断言页（serve 后打开，title=PASS 即绿）：
  `tests/assert_data.html`（32 项）· `tests/assert_reader.html`（22 项，iframe 驱动真
  index：深链/循读/岁时/检索）· `tests/assert_map.html`（22 项，分层开关/符号计数）·
  `tests/assert_p2.html`（29 项，双桥数据/导出同口径/SW 键对齐）。
- CI：`.github/workflows/ci.yml`（push/PR）；周六审计 `audit.yml`（10:50 CST 错峰，
  含真断网离线三验）。

## 目录

```
index.html              # 入口（舆图/循读/名录/岁时/计量/关于）
js/                     # config→map→rail→reader→search→suishi→stats→bookmarks→export→app（defer 序）
data/                   # site_data.js(勿手改) · sections.js · stats.js · text/v0..v10
data_raw/               # kanripo 原始页留档（不入 git）
tools/                  # fetch→parse→stats→build→lint→export→sums→paper→xref→offline
tests/                  # 断言页
docs/                   # ANALYSIS.md · stats.json · 论文 PDF · figs/ · img/
exports/                # CSV×3 + KML + GeoJSON（P2）
```

## 站际桥（相对兄弟路径）

双桥深链用 `../TPHY/#zhou=…`、`../LYGL/#m=map` 等**相对兄弟路径**——约定父目录
（D:\W_A_W）同根服务：`cd D:\W_A_W && python -m http.server` 后 /MHJH/ /TPHY/ 同源可达。
姊妹站一律只读。

## 许可

代码与自绘数据：MIT；文本为公版古籍（四库本影印整理，kanripo 转录）。
