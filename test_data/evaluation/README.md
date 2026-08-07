# AI 分析评估样本

`generate_samples.py` 生成 20 条教育行业人工标注样本，覆盖成交、流失和持续跟进三种真实业务结果，并为每条样本提供期望客户等级及完整画像参考。

```bash
python -m test_data.evaluation.generate_samples
```

`analysis_record_id` 是演示关联值。真实评估时应根据 `conversation_external_id` 找到对应的最新 `AIAnalysisRecord`，再替换为实际记录 ID。
