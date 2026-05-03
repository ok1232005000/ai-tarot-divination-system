# 测试方案简述

本实验覆盖以下测试技术：

- 单元测试：`tests/test_tarot_card.py`、`tests/test_spread.py`
- 黑盒测试：`test_black_white_box.py` 中 `TestBlackBox`
- 白盒测试：`test_black_white_box.py` 中 `TestWhiteBox`
- 决策表测试：`tests/test_decision_table.py` + `tests/decision_table.md`
- 冒烟测试：`test_basic.py`

统一执行命令：

```bash
python -m unittest discover -v
```
