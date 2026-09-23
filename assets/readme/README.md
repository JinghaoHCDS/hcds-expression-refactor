# README 宣传图与动画

正式首图采用已确认的“排句”方案：口头填充在挡板前停住并淡出，有内容的句子按“感受—痛点—办法”归位，每段附简短作用说明。上半部分标题加粗。图中文字是改写演示，不是模型效果实测。

仅沿用个人配色：雾蓝 `#BECBEB`、卡布里蓝 `#0C91FA`、麦黄 `#EBCB75`、墨灰 `#343A46`、纸白 `#F7F7F4`。使用系统无衬线字体，不分发字体二进制。

- `hero.svg`：完成状态的静态版本，支持缩放。
- `hero.gif`：README 自动播放的动画，1200 × 620、20 FPS、9 秒循环，约 894 KB。
- `../../scripts/readme/build_hero.py`：文案、布局和时间函数的源文件，两种产物从同一套规则生成。
- `../../scripts/readme/render_svg_frames.cjs`：将 SVG 帧栅格化，最终由 FFmpeg 编码为 GIF。

README 通过 `<picture>` 为减少动态效果偏好提供静态 SVG，并保留直接打开静态图的链接。GIF 不依赖运行脚本即可播放。示例词语只表示当前语境中的无意义填充，不是机械禁词表。

## 重新生成首图

需要 Python 3、Node.js、FFmpeg。渲染依赖可安装在临时目录，不给 Skill 或提示词构建增加依赖。在仓库根目录运行：

```bash
npm install --prefix /tmp/hcds-svg-render --no-audit --no-fund @resvg/resvg-js@2.6.2
python3 scripts/readme/build_hero.py \
  --renderer-module /tmp/hcds-svg-render/node_modules/@resvg/resvg-js
```

修改文案、几何或动画时序后运行以上命令，会更新 `hero.svg` 和 `hero.gif`。只手改生成后的 SVG 不会同步动画。

渲染器在 `fc-match` 可用时只载入所需字体以加快构建，否则使用系统字体发现。不同系统字形可能不同；已生成的 GIF 固化本次结果。

完整提示词仍独立使用 `python3 scripts/build_prompt.py` 生成，使用 `python3 scripts/build_prompt.py --check` 校验。
