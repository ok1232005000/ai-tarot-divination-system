# 软件测试决策表（课程实验）

## 1) EEG 情绪判定决策表

| 规则 | beta > 20 且 alpha < 8 | beta < 15 且 alpha > 10 | theta > 6 且 alpha < 8 | beta > 15 且 alpha > 8 | 期望情绪 |
|---|---|---|---|---|---|
| R1 | Y | N | N | N | 焦虑 |
| R2 | N | Y | N | N | 放松 |
| R3 | N | N | Y | N | 疲劳 |
| R4 | N | N | N | Y | 专注 |
| R5 | N | N | N | N | 中性/平静（由后续分支决定） |

## 2) ReadingSession 输入有效性决策表

| 规则 | 问题长度 >= 10 | 问题长度 <= 500 | spread_type 非空 | cards_drawn 非空 | 卡牌不重复 | feedback_rating 在[1,5]或空 | 结果 |
|---|---|---|---|---|---|---|---|
| RS1 | Y | Y | Y | Y | Y | Y | 通过 |
| RS2 | N | Y | Y | Y | Y | Y | 拒绝 |
| RS3 | Y | N | Y | Y | Y | Y | 拒绝 |
| RS4 | Y | Y | N | Y | Y | Y | 拒绝 |
| RS5 | Y | Y | Y | N | Y | Y | 拒绝 |
| RS6 | Y | Y | Y | Y | N | Y | 拒绝 |
| RS7 | Y | Y | Y | Y | Y | N | 拒绝 |
