from pathlib import Path

import pandas as pd


FILE_PATH = "学生问卷172份.xlsx"
SHEET_NAME = "Sheet1"
ATTENTION_CHECK_COLUMN = '15、为了确保问卷质量,请在本题选择"基本同意":'
ATTENTION_CHECK_EXPECTED = '基本同意 ←请选择此项'
SINGLE_CHOICE_QUESTIONS = ["Q1", "Q2", "Q4", "Q5"]
MULTI_SELECT_QUESTIONS = ["Q3", "Q7", "Q8", "Q11", "Q12", "Q13"]


def split_multi_select_answers(series, separator="┋"):
	clean_series = series.dropna().astype(str)
	split_answers = []
	for value in clean_series:
		parts = [part.strip() for part in value.split(separator) if part.strip()]
		split_answers.extend(parts)
	return clean_series, split_answers


def normalize_label(text):
	return " ".join(str(text).split())


def load_excel_data(file_path=FILE_PATH, sheet_name=SHEET_NAME):
	return pd.read_excel(file_path, sheet_name=sheet_name)


def print_basic_inspection(df):
	print("1) 数据行列数")
	print(df.shape)
	print()

	print("2) 列名清单")
	print(df.columns.tolist())
	print()


def filter_valid_questionnaires(
	df,
	attention_check_column=ATTENTION_CHECK_COLUMN,
	attention_check_expected=ATTENTION_CHECK_EXPECTED,
):
	valid_df = df[df[attention_check_column] == attention_check_expected].copy()
	invalid_count = len(df) - len(valid_df)

	print("步骤2：过滤无效问卷")
	print("本步服务交付目标：统一全流程有效样本口径")
	print("验收信号：")
	print(f"- 总问卷数 = {len(df)}")
	print(f"- 有效问卷数 = {len(valid_df)}")
	print(f"- 无效问卷数 = {invalid_count}")
	print(f"- 注意力检查正确值 = {attention_check_expected}")
	print()

	return valid_df, invalid_count


def build_question_column_mapping(df, attention_check_column=ATTENTION_CHECK_COLUMN):
	question_column_mapping = {
		"Q1": next(column for column in df.columns if column.startswith("1、")),
		"Q2": next(column for column in df.columns if column.startswith("2、")),
		"Q3": next(column for column in df.columns if column.startswith("3、")),
		"Q4": next(column for column in df.columns if column.startswith("4、")),
		"Q5": next(column for column in df.columns if column.startswith("5、")),
		"Q6": next(column for column in df.columns if column.startswith("6、")),
		"Q7": next(column for column in df.columns if column.startswith("7、")),
		"Q8": next(column for column in df.columns if column.startswith("8、")),
		"Q15": attention_check_column,
	}

	question_column_mapping["Q9"] = [column for column in df.columns if column.startswith("9、")]
	question_column_mapping["Q10"] = [column for column in df.columns if column.startswith("10、")]
	question_column_mapping["Q11"] = next(column for column in df.columns if column.startswith("11、"))
	question_column_mapping["Q12"] = next(column for column in df.columns if column.startswith("12、"))
	question_column_mapping["Q13"] = next(column for column in df.columns if column.startswith("13、"))
	question_column_mapping["Q14"] = next(column for column in df.columns if column.startswith("14、"))

	print("步骤1：锁定题号与真实列名映射")
	print("本步服务交付目标：固定后续统计与清洗所依赖的题号取列口径")
	print("验收信号：")
	for question_no in ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q11", "Q12", "Q13", "Q14", "Q15"]:
		print(f"- {question_no} -> {question_column_mapping[question_no]}")
	print(f"- Q9 列数 = {len(question_column_mapping['Q9'])}")
	print(f"- Q10 列数 = {len(question_column_mapping['Q10'])}")
	print()

	return question_column_mapping


def analyze_single_choice_questions(valid_df, question_column_mapping):
	print("步骤3：确认单选题可直接统计")
	print("本步服务交付目标：为 Q1、Q2、Q4、Q5 的频率分布交付准备可直接统计的有效样本")
	print("验收信号：")

	single_choice_stats = {}
	for question_no in SINGLE_CHOICE_QUESTIONS:
		column_name = question_column_mapping[question_no]
		answer_series = valid_df[column_name].dropna()
		frequency_table = answer_series.value_counts()
		print(f"- {question_no} 有效作答数 = {len(answer_series)}")
		print(f"- {question_no} 类别数 = {len(frequency_table)}")
		print(f"- {question_no} 频数合计 = {int(frequency_table.sum())}")

		single_choice_stats[question_no] = pd.DataFrame(
			{
				"option": frequency_table.index,
				"count": frequency_table.values,
				"rate": frequency_table.values / len(valid_df),
			}
		)

	print()
	return single_choice_stats


def analyze_multi_select_questions(valid_df, question_column_mapping):
	print("步骤4：拆分多选题为选项级数据")
	print("本步服务交付目标：为 Q3、Q7、Q8、Q11、Q12、Q13 的选择次数与选择率交付准备可统计的选项级数据")
	print("验收信号：")

	multi_select_stats = {}
	for question_no in MULTI_SELECT_QUESTIONS:
		column_name = question_column_mapping[question_no]
		raw_answers, split_answers = split_multi_select_answers(valid_df[column_name])
		option_count = len(set(split_answers))
		print(f"- {question_no} 原始列形态 = 单列多选")
		print(f"- {question_no} 有效作答数 = {len(raw_answers)}")
		print(f"- {question_no} 拆分后选项数 = {option_count}")
		print(f"- {question_no} 总选择次数 = {len(split_answers)}")
		print(f"- {question_no} 选择率分母 = {len(valid_df)}")

		count_series = pd.Series(split_answers).value_counts()
		multi_select_stats[question_no] = pd.DataFrame(
			{
				"option": count_series.index,
				"count": count_series.values,
				"rate": count_series.values / len(valid_df),
			}
		)

	print()
	return multi_select_stats


def analyze_q6_labels_and_scores(valid_df, question_column_mapping):
	q6_raw_answers = valid_df[question_column_mapping["Q6"]].dropna().astype(str)
	q6_raw_labels = []
	for value in q6_raw_answers:
		parts = [part.strip() for part in value.split("→") if part.strip()]
		q6_raw_labels.extend(parts)

	print("步骤5：标准化多选题与排序题标签")
	print("本步服务交付目标：为多选题统计和 Q6 偏好得分交付准备稳定且不重复的标签口径")
	print("验收信号：")
	for question_no in MULTI_SELECT_QUESTIONS:
		column_name = question_column_mapping[question_no]
		_, split_answers = split_multi_select_answers(valid_df[column_name])
		raw_label_count = len(set(split_answers))
		normalized_label_count = len({normalize_label(label) for label in split_answers})
		print(f"- {question_no} 标准化前类别数 = {raw_label_count}")
		print(f"- {question_no} 标准化后类别数 = {normalized_label_count}")

	q6_normalized_labels = {normalize_label(label) for label in q6_raw_labels}
	print(f"- Q6 标准化前类型数 = {len(set(q6_raw_labels))}")
	print(f"- Q6 标准化后类型数 = {len(q6_normalized_labels)}")
	print()

	q6_weight_by_rank = {1: 3, 2: 2, 3: 1}
	q6_weighted_scores = {}
	q6_rank_counts = {1: 0, 2: 0, 3: 0}

	for value in q6_raw_answers:
		parts = [normalize_label(part) for part in value.split("→") if part.strip()]
		for rank, label in enumerate(parts[:3], start=1):
			q6_rank_counts[rank] += 1
			q6_weighted_scores[label] = q6_weighted_scores.get(label, 0) + q6_weight_by_rank[rank]

	print("步骤6：解析 Q6 排序顺位并计算加权偏好")
	print("本步服务交付目标：为 Q6 的9种实践成果类型偏好得分排名交付准备可直接汇总的加权分数")
	print("验收信号：")
	print(f"- Q6 识别到的成果类型数 = {len(q6_weighted_scores)}")
	print(f"- Q6 加权规则 = 第1选×{q6_weight_by_rank[1]}，第2选×{q6_weight_by_rank[2]}，第3选×{q6_weight_by_rank[3]}")
	print(f"- Q6 第1位记录数 = {q6_rank_counts[1]}")
	print(f"- Q6 第2位记录数 = {q6_rank_counts[2]}")
	print(f"- Q6 第3位记录数 = {q6_rank_counts[3]}")
	print(f"- Q6 已生成总分的成果类型数 = {len(q6_weighted_scores)}")
	print()

	q6_weighted_score_table = pd.DataFrame(
		[
			{"option": option, "weighted_score": score}
			for option, score in q6_weighted_scores.items()
		]
	).sort_values(by="weighted_score", ascending=False, ignore_index=True)

	return q6_raw_answers, q6_weighted_score_table


def validate_q9_q10_numeric_inputs(valid_df, question_column_mapping):
	q9_columns = question_column_mapping["Q9"]
	q10_columns = question_column_mapping["Q10"]
	q9_min_value = int(valid_df[q9_columns].min().min())
	q9_max_value = int(valid_df[q9_columns].max().max())
	q9_invalid_value_count = int(((valid_df[q9_columns] < 1) | (valid_df[q9_columns] > 5)).sum().sum())
	q10_row_sums = valid_df[q10_columns].sum(axis=1)
	q10_invalid_row_count = int((q10_row_sums != 100).sum())

	print("步骤7：校验 Q9 与 Q10 数值合法性")
	print("本步服务交付目标：为 Q9 的均值/分布分析和 Q10 的平均权重分析准备可直接使用的数值型底表")
	print("验收信号：")
	print(f"- Q9 维度数 = {len(q9_columns)}")
	print(f"- Q9 分值范围 = {q9_min_value}-{q9_max_value}")
	print(f"- Q9 异常值数 = {q9_invalid_value_count}")
	print(f"- Q10 主体数 = {len(q10_columns)}")
	print(f"- Q10 每行权重和唯一值 = {sorted(q10_row_sums.unique().tolist())}")
	print(f"- Q10 异常行数 = {q10_invalid_row_count}")
	print()

	q9_mean_table = valid_df[q9_columns].mean().sort_values(ascending=False).reset_index()
	q9_mean_table.columns = ["dimension", "mean_score"]

	q10_mean_weight_table = valid_df[q10_columns].mean().reset_index()
	q10_mean_weight_table.columns = ["stakeholder", "mean_weight"]

	return q9_mean_table, q10_mean_weight_table


def summarize_cleaning_stage(single_choice_stats, multi_select_stats, q6_weighted_score_table, q9_mean_table, q10_mean_weight_table):
	print("步骤8：生成清洗阶段最终统计结果")
	print("本步服务交付目标：为各题图表绘制和 descriptive_summary 汇总准备最终统计表")
	print("验收信号：")
	print(f"- 单选题统计表数 = {len(single_choice_stats)}")
	print(f"- 多选题统计表数 = {len(multi_select_stats)}")
	print(f"- Q6 加权得分表行数 = {len(q6_weighted_score_table)}")
	print(f"- Q9 均值表行数 = {len(q9_mean_table)}")
	print(f"- Q10 平均权重表行数 = {len(q10_mean_weight_table)}")
	print(f"- 已覆盖题号 = {sorted(single_choice_stats.keys()) + sorted(multi_select_stats.keys()) + ['Q6', 'Q9', 'Q10']}")
	print()


def run_consistency_check(valid_df, single_choice_stats, multi_select_stats):
	expected_question_coverage = {
		"Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12", "Q13"
	}
	actual_question_coverage = set(single_choice_stats.keys()) | set(multi_select_stats.keys()) | {"Q6", "Q9", "Q10"}
	missing_questions = sorted(expected_question_coverage - actual_question_coverage)
	unexpected_questions = sorted(actual_question_coverage - expected_question_coverage)
	single_choice_total_ok = all(int(table["count"].sum()) == len(valid_df) for table in single_choice_stats.values())

	print("步骤10：最终一致性检查")
	print("本步服务交付目标：确认清洗阶段产生的统计结果使用的是同一套样本口径和题号覆盖")
	print("验收信号：")
	print(f"- 有效样本数一致 = {single_choice_total_ok}")
	print(f"- 题号缺失列表 = {missing_questions}")
	print(f"- 题号额外列表 = {unexpected_questions}")
	print(f"- 一致性检查通过 = {single_choice_total_ok and not missing_questions and not unexpected_questions}")
	print()


def save_cleaning_outputs(df, valid_df, invalid_count, question_column_mapping, q6_raw_answers):
	output_dir = Path("output")
	output_dir.mkdir(exist_ok=True)
	cleaned_data_output_path = output_dir / "cleaned_data.csv"
	valid_df.to_csv(cleaned_data_output_path, index=False, encoding="utf-8-sig")

	q6_ranked_rows = []
	for value in q6_raw_answers:
		parts = [normalize_label(part) for part in value.split("→") if part.strip()]
		q6_ranked_rows.append(
			{
				"第1选": parts[0] if len(parts) > 0 else None,
				"第2选": parts[1] if len(parts) > 1 else None,
				"第3选": parts[2] if len(parts) > 2 else None,
			}
		)

	q6_ranked_df = pd.DataFrame(q6_ranked_rows)
	q6_ranked_output_path = output_dir / "q6_ranked.csv"
	q6_ranked_df.to_csv(q6_ranked_output_path, index=False, encoding="utf-8-sig")

	multi_choice_binary_df = pd.DataFrame(index=valid_df.index)
	for question_no in MULTI_SELECT_QUESTIONS:
		column_name = question_column_mapping[question_no]
		parsed_answers = valid_df[column_name].fillna("").astype(str).apply(
			lambda value: [normalize_label(part) for part in value.split("┋") if part.strip()]
		)
		all_options = sorted({option for answers in parsed_answers for option in answers})
		for option in all_options:
			binary_column_name = f"{question_no}__{option}"
			multi_choice_binary_df[binary_column_name] = parsed_answers.apply(lambda answers: int(option in answers))

	multi_choice_binary_output_path = output_dir / "multi_choice_binary.csv"
	multi_choice_binary_df.to_csv(multi_choice_binary_output_path, index=False, encoding="utf-8-sig")

	invalid_attention_values = df.loc[
		df[ATTENTION_CHECK_COLUMN] != ATTENTION_CHECK_EXPECTED,
		ATTENTION_CHECK_COLUMN,
	].fillna("<缺失>").astype(str).value_counts()

	cleaning_report_lines = [
		"清洗日志",
		f"原始行数: {len(df)}",
		f"有效行数: {len(valid_df)}",
		f"无效行数: {invalid_count}",
		"",
		"无效原因统计:",
		f"- 注意力检查未选择指定答案: {invalid_count}",
		"",
		"注意力检查未通过的原始取值分布:",
	]
	for label, count in invalid_attention_values.items():
		cleaning_report_lines.append(f"- {label}: {count}")

	cleaning_report_output_path = output_dir / "cleaning_report.txt"
	cleaning_report_output_path.write_text("\n".join(cleaning_report_lines), encoding="utf-8")

	print("步骤9：保存清洗阶段中间文件")
	print("本步服务交付目标：将前面已经生成的中间结果统一落盘为可交付文件")
	print("验收信号：")
	print(f"- 已保存 {cleaned_data_output_path}")
	print(f"- 已保存 {q6_ranked_output_path}")
	print(f"- 已保存 {multi_choice_binary_output_path}")
	print(f"- 已保存 {cleaning_report_output_path}")


def main():
	df = load_excel_data()
	print_basic_inspection(df)
	question_column_mapping = build_question_column_mapping(df)
	valid_df, invalid_count = filter_valid_questionnaires(df)
	single_choice_stats = analyze_single_choice_questions(valid_df, question_column_mapping)
	multi_select_stats = analyze_multi_select_questions(valid_df, question_column_mapping)
	q6_raw_answers, q6_weighted_score_table = analyze_q6_labels_and_scores(valid_df, question_column_mapping)
	q9_mean_table, q10_mean_weight_table = validate_q9_q10_numeric_inputs(valid_df, question_column_mapping)
	summarize_cleaning_stage(single_choice_stats, multi_select_stats, q6_weighted_score_table, q9_mean_table, q10_mean_weight_table)
	save_cleaning_outputs(df, valid_df, invalid_count, question_column_mapping, q6_raw_answers)
	run_consistency_check(valid_df, single_choice_stats, multi_select_stats)


if __name__ == "__main__":
	main()