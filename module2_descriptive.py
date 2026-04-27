from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


CLEANED_DATA_PATH = Path("output") / "cleaned_data.csv"
MULTI_CHOICE_BINARY_PATH = Path("output") / "multi_choice_binary.csv"
Q6_RANKED_PATH = Path("output") / "q6_ranked.csv"
OUTPUT_DIR = Path("output")
SINGLE_CHOICE_QUESTIONS = ["Q1", "Q2", "Q4", "Q5"]
MULTI_SELECT_QUESTIONS = ["Q3", "Q7", "Q8", "Q11", "Q12", "Q13"]


def configure_matplotlib_fonts():
	plt.rcParams["font.sans-serif"] = [
		"Microsoft YaHei",
		"SimHei",
		"Noto Sans CJK SC",
		"Arial Unicode MS",
	]
	plt.rcParams["axes.unicode_minus"] = False


def load_cleaned_data(file_path=CLEANED_DATA_PATH):
	return pd.read_csv(file_path)


def load_multi_choice_binary_data(file_path=MULTI_CHOICE_BINARY_PATH):
	return pd.read_csv(file_path)


def load_q6_ranked_data(file_path=Q6_RANKED_PATH):
	return pd.read_csv(file_path)


def build_question_column_mapping(df):
	return {
		"Q1": next(column for column in df.columns if column.startswith("1、")),
		"Q2": next(column for column in df.columns if column.startswith("2、")),
		"Q4": next(column for column in df.columns if column.startswith("4、")),
		"Q5": next(column for column in df.columns if column.startswith("5、")),
		"Q9": [column for column in df.columns if column.startswith("9、")],
		"Q10": [column for column in df.columns if column.startswith("10、")],
	}


def prepare_single_choice_table(df, column_name):
	answer_series = df[column_name].dropna().astype(str).str.strip()
	answer_series = answer_series[answer_series != ""]
	frequency_table = answer_series.value_counts()
	return pd.DataFrame(
		{
			"option": frequency_table.index,
			"count": frequency_table.values,
			"rate": frequency_table.values / len(df),
		}
	)


def plot_single_choice_question(question_no, question_title, stats_df, output_path):
	figure, axes = plt.subplots(1, 2, figsize=(14, 6))
	bar_ax, pie_ax = axes

	bar_ax.bar(stats_df["option"], stats_df["count"], color="#4C78A8")
	bar_ax.set_title(f"{question_no} 频数分布")
	bar_ax.set_ylabel("频数")
	bar_ax.tick_params(axis="x", rotation=25)

	for index, count in enumerate(stats_df["count"]):
		bar_ax.text(index, count, str(int(count)), ha="center", va="bottom", fontsize=9)

	pie_labels = [f"{option}\n{rate:.1%}" for option, rate in zip(stats_df["option"], stats_df["rate"])]
	pie_ax.pie(stats_df["count"], labels=pie_labels, startangle=90, counterclock=False)
	pie_ax.set_title(f"{question_no} 占比分布")

	figure.suptitle(question_title)
	figure.tight_layout()
	figure.savefig(output_path, dpi=200, bbox_inches="tight")
	plt.close(figure)


def generate_single_choice_charts(df, question_column_mapping):
	OUTPUT_DIR.mkdir(exist_ok=True)

	print("步骤1：绘制单选题频率分布图（Q1、Q2、Q4、Q5）")
	print(f"本步输入：{CLEANED_DATA_PATH}")
	print("本步输出：output/desc_q1.png、output/desc_q2.png、output/desc_q4.png、output/desc_q5.png")
	print("终端验收信号：打印 Q1/Q2/Q4/Q5 频数统计完成，并分别打印每题有效样本数、选项数、图片保存路径")

	for question_no in SINGLE_CHOICE_QUESTIONS:
		column_name = question_column_mapping[question_no]
		stats_df = prepare_single_choice_table(df, column_name)
		output_path = OUTPUT_DIR / f"desc_{question_no.lower()}.png"
		plot_single_choice_question(question_no, column_name, stats_df, output_path)

		print(f"- {question_no} 有效样本数 = {int(stats_df['count'].sum())}")
		print(f"- {question_no} 选项数 = {len(stats_df)}")
		print(f"- {question_no} 已保存 {output_path}")

	print("Q1/Q2/Q4/Q5 频数统计完成")


def build_multi_select_column_mapping(df):
	column_mapping = {}
	for question_no in MULTI_SELECT_QUESTIONS:
		prefix = f"{question_no}__"
		column_mapping[question_no] = [column for column in df.columns if column.startswith(prefix)]
	return column_mapping


def prepare_multi_select_table(df, question_no, question_columns):
	question_df = df[question_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
	count_series = question_df.sum(axis=0).sort_values(ascending=True)
	stats_df = pd.DataFrame(
		{
			"option": [column.split("__", 1)[1] for column in count_series.index],
			"count": count_series.values,
			"rate": count_series.values / len(df),
		}
	)
	stats_df["question_no"] = question_no
	return stats_df


def plot_multi_select_question(question_no, stats_df, output_path):
	figure, ax = plt.subplots(figsize=(12, max(6, len(stats_df) * 0.6)))
	ax.barh(stats_df["option"], stats_df["count"], color="#59A14F")
	ax.set_title(f"{question_no} 选择次数与选择率")
	ax.set_xlabel("选择次数")

	for index, row in stats_df.reset_index(drop=True).iterrows():
		ax.text(
			row["count"],
			index,
			f" {int(row['count'])} ({row['rate']:.1%})",
			va="center",
			fontsize=9,
		)

	figure.tight_layout()
	figure.savefig(output_path, dpi=200, bbox_inches="tight")
	plt.close(figure)


def generate_multi_select_charts(df):
	column_mapping = build_multi_select_column_mapping(df)

	print()
	print("步骤2：绘制多选题选择次数与选择率水平条形图（Q3、Q7、Q8、Q11、Q12、Q13）")
	print(f"本步输入：{MULTI_CHOICE_BINARY_PATH}")
	print("本步输出：output/desc_q3.png、output/desc_q7.png、output/desc_q8.png、output/desc_q11.png、output/desc_q12.png、output/desc_q13.png")
	print("终端验收信号：打印 Q3/Q7/Q8/Q11/Q12/Q13 多选统计完成，并逐题打印识别到的列数、各题总选择次数、图片保存路径")

	for question_no in MULTI_SELECT_QUESTIONS:
		question_columns = column_mapping[question_no]
		stats_df = prepare_multi_select_table(df, question_no, question_columns)
		output_path = OUTPUT_DIR / f"desc_{question_no.lower()}.png"
		plot_multi_select_question(question_no, stats_df, output_path)

		print(f"- {question_no} 识别到的列数 = {len(question_columns)}")
		print(f"- {question_no} 总选择次数 = {int(stats_df['count'].sum())}")
		print(f"- {question_no} 已保存 {output_path}")

	print("Q3/Q7/Q8/Q11/Q12/Q13 多选统计完成")


def simplify_q9_dimension_label(column_name):
	label = column_name.split("—", 1)[-1] if "—" in column_name else column_name.split("9、", 1)[-1]
	label = label.split(":", 1)[0]
	return label.strip()


def prepare_q9_mean_table(df, q9_columns):
	q9_df = df[q9_columns].apply(pd.to_numeric, errors="coerce")
	mean_series = q9_df.mean().sort_values(ascending=False)
	return pd.DataFrame(
		{
			"dimension": [simplify_q9_dimension_label(column) for column in mean_series.index],
			"mean_score": mean_series.values,
		}
	)


def plot_q9_radar_chart_on_axis(stats_df, ax):
	angles = [index / float(len(stats_df)) * 2 * 3.141592653589793 for index in range(len(stats_df))]
	angles += angles[:1]

	values = stats_df["mean_score"].tolist()
	values += values[:1]
	labels = stats_df["dimension"].tolist()

	ax.plot(angles, values, color="#E15759", linewidth=2)
	ax.fill(angles, values, color="#E15759", alpha=0.25)
	ax.set_xticks(angles[:-1])
	ax.set_xticklabels(labels)
	ax.set_ylim(0, 5)
	ax.set_yticks([1, 2, 3, 4, 5])
	ax.set_title("Q9 重要性维度均值雷达图", pad=28)


def prepare_q9_long_table(df, q9_columns):
	q9_df = df[q9_columns].apply(pd.to_numeric, errors="coerce")
	rename_mapping = {column: simplify_q9_dimension_label(column) for column in q9_columns}
	q9_long_df = q9_df.rename(columns=rename_mapping).melt(
		var_name="dimension",
		value_name="score",
	).dropna(subset=["score"])
	return q9_long_df


def plot_q9_boxplot_on_axis(q9_long_df, ax):
	dimension_order = (
		q9_long_df.groupby("dimension")["score"]
		.mean()
		.sort_values(ascending=False)
		.index
		.tolist()
	)
	data_by_dimension = [
		q9_long_df.loc[q9_long_df["dimension"] == dimension, "score"].tolist()
		for dimension in dimension_order
	]

	boxplot = ax.boxplot(data_by_dimension, patch_artist=True, tick_labels=dimension_order)
	for patch in boxplot["boxes"]:
		patch.set_facecolor("#F28E2B")
		patch.set_alpha(0.65)

	ax.set_title("Q9 重要性维度得分分布箱线图")
	ax.set_ylabel("评分")
	ax.set_ylim(1, 5)
	ax.tick_params(axis="x", rotation=25)


def generate_q9_combined_chart(df, question_column_mapping):
	q9_columns = question_column_mapping["Q9"]
	q9_mean_df = prepare_q9_mean_table(df, q9_columns)
	q9_long_df = prepare_q9_long_table(df, q9_columns)
	output_path = OUTPUT_DIR / "desc_q9.png"
	per_dimension_counts = q9_long_df.groupby("dimension")["score"].count()

	figure = plt.figure(figsize=(17, 8))
	radar_ax = figure.add_subplot(1, 2, 1, polar=True)
	boxplot_ax = figure.add_subplot(1, 2, 2)
	plot_q9_radar_chart_on_axis(q9_mean_df, radar_ax)
	plot_q9_boxplot_on_axis(q9_long_df, boxplot_ax)
	figure.tight_layout()
	figure.savefig(output_path, dpi=200, bbox_inches="tight")
	plt.close(figure)

	print()
	print("步骤3-4：绘制 Q9 组合图（雷达图 + 箱线图）")
	print(f"本步输入：{CLEANED_DATA_PATH}")
	print("本步输出：output/desc_q9.png")
	print("终端验收信号：打印 Q9 组合图完成，并输出 10 个维度的均值表、每维非空样本数、图片保存路径")
	print(f"- Q9 维度数量 = {len(q9_mean_df)}")
	print("- Q9 均值表：")
	for _, row in q9_mean_df.iterrows():
		print(f"  - {row['dimension']} = {row['mean_score']:.2f}")
	print(f"- Q9 参与作图维度数 = {per_dimension_counts.shape[0]}")
	print("- Q9 每维非空样本数：")
	for dimension, count in per_dimension_counts.items():
		print(f"  - {dimension} = {int(count)}")
	print(f"- Q9 已保存 {output_path}")
	print("Q9 组合图完成")


def simplify_q10_stakeholder_label(column_name):
	label = column_name.split("—", 1)[-1] if "—" in column_name else column_name.split("10、", 1)[-1]
	return label.strip()


def prepare_q10_mean_weight_table(df, q10_columns):
	q10_df = df[q10_columns].apply(pd.to_numeric, errors="coerce")
	mean_series = q10_df.mean()
	return pd.DataFrame(
		{
			"stakeholder": [simplify_q10_stakeholder_label(column) for column in mean_series.index],
			"mean_weight": mean_series.values,
		}
	)


def plot_q10_mean_weight_chart(stats_df, output_path):
	figure, ax = plt.subplots(figsize=(6.5, 8.5))
	colors = ["#4C78A8", "#F58518", "#E45756", "#72B7B2", "#54A24B"]
	bottom = 0.0

	for (_, row), color in zip(stats_df.iterrows(), colors):
		ax.bar(["平均权重分配"], [row["mean_weight"]], bottom=bottom, color=color, label=row["stakeholder"])
		ax.text(
			0,
			bottom + row["mean_weight"] / 2,
			f"{row['stakeholder']}\n{row['mean_weight']:.1f}%",
			ha="center",
			va="center",
			fontsize=9,
		)
		bottom += row["mean_weight"]

	ax.set_ylim(0, 100)
	ax.set_ylabel("平均权重（%）")
	ax.set_title("Q10 多主体平均权重分配")
	ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=3, frameon=False)

	figure.tight_layout()
	figure.savefig(output_path, dpi=200, bbox_inches="tight")
	plt.close(figure)


def generate_q10_mean_weight_chart(df, question_column_mapping):
	q10_columns = question_column_mapping["Q10"]
	stats_df = prepare_q10_mean_weight_table(df, q10_columns)
	output_path = OUTPUT_DIR / "desc_q10.png"
	plot_q10_mean_weight_chart(stats_df, output_path)
	mean_weight_sum = stats_df["mean_weight"].sum()

	print()
	print("步骤5：绘制 Q10 多主体平均权重堆积条形图")
	print(f"本步输入：{CLEANED_DATA_PATH}")
	print("本步输出：output/desc_q10.png")
	print("终端验收信号：打印 Q10 权重图完成，并输出 5 个主体平均权重、均值合计、图片保存路径")
	print("- Q10 平均权重表：")
	for _, row in stats_df.iterrows():
		print(f"  - {row['stakeholder']} = {row['mean_weight']:.2f}")
	print(f"- Q10 均值合计 = {mean_weight_sum:.2f}")
	print(f"- Q10 已保存 {output_path}")
	print("Q10 权重图完成")


def prepare_q6_weighted_score_table(df):
	rank_weights = {"第1选": 3, "第2选": 2, "第3选": 1}
	weighted_scores = {}

	for rank_column, weight in rank_weights.items():
		answer_series = df[rank_column].dropna().astype(str).str.strip()
		answer_series = answer_series[answer_series != ""]
		for option in answer_series:
			weighted_scores[option] = weighted_scores.get(option, 0) + weight

	stats_df = pd.DataFrame(
		[
			{"option": option, "weighted_score": score}
			for option, score in weighted_scores.items()
		]
	).sort_values(by="weighted_score", ascending=False, ignore_index=True)
	return stats_df


def plot_q6_weighted_score_chart(stats_df, output_path):
	figure, ax = plt.subplots(figsize=(14, max(6, len(stats_df) * 0.5)))
	ax.barh(stats_df["option"][::-1], stats_df["weighted_score"][::-1], color="#B279A2")
	ax.set_title("Q6 实践成果类型加权偏好得分")
	ax.set_xlabel("加权得分")

	for index, row in stats_df.iloc[::-1].reset_index(drop=True).iterrows():
		ax.text(row["weighted_score"], index, f" {int(row['weighted_score'])}", va="center", fontsize=9)

	figure.tight_layout()
	figure.savefig(output_path, dpi=200, bbox_inches="tight")
	plt.close(figure)


def generate_q6_weighted_score_chart(df):
	stats_df = prepare_q6_weighted_score_table(df)
	output_path = OUTPUT_DIR / "desc_q6.png"
	plot_q6_weighted_score_chart(stats_df, output_path)

	print()
	print("步骤6：绘制 Q6 排序题加权偏好得分柱状图")
	print(f"本步输入：{Q6_RANKED_PATH}")
	print("本步输出：output/desc_q6.png")
	print("终端验收信号：打印 Q6 加权得分完成，并输出识别到的成果类型数量、每类总得分、图片保存路径")
	print(f"- Q6 识别到的成果类型数量 = {len(stats_df)}")
	print("- Q6 每类总得分：")
	for _, row in stats_df.iterrows():
		print(f"  - {row['option']} = {int(row['weighted_score'])}")
	print(f"- Q6 已保存 {output_path}")
	print("Q6 加权得分完成")


def build_descriptive_summary(
	cleaned_df,
	multi_choice_binary_df,
	q6_ranked_df,
	question_column_mapping,
):
	summary_tables = []

	for question_no in SINGLE_CHOICE_QUESTIONS:
		column_name = question_column_mapping[question_no]
		stats_df = prepare_single_choice_table(cleaned_df, column_name).copy()
		stats_df.insert(0, "question_no", question_no)
		stats_df.insert(1, "metric_type", "single_choice_frequency")
		stats_df.rename(columns={"option": "label", "count": "value"}, inplace=True)
		summary_tables.append(stats_df[["question_no", "metric_type", "label", "value", "rate"]])

	column_mapping = build_multi_select_column_mapping(multi_choice_binary_df)
	for question_no in MULTI_SELECT_QUESTIONS:
		stats_df = prepare_multi_select_table(multi_choice_binary_df, question_no, column_mapping[question_no]).copy()
		stats_df.insert(1, "metric_type", "multi_select_frequency")
		stats_df.rename(columns={"option": "label", "count": "value"}, inplace=True)
		summary_tables.append(stats_df[["question_no", "metric_type", "label", "value", "rate"]])

	q9_mean_df = prepare_q9_mean_table(cleaned_df, question_column_mapping["Q9"]).copy()
	q9_mean_df.insert(0, "question_no", "Q9")
	q9_mean_df.insert(1, "metric_type", "mean_score")
	q9_mean_df.rename(columns={"dimension": "label", "mean_score": "value"}, inplace=True)
	q9_mean_df["rate"] = pd.NA
	summary_tables.append(q9_mean_df[["question_no", "metric_type", "label", "value", "rate"]])

	q10_mean_df = prepare_q10_mean_weight_table(cleaned_df, question_column_mapping["Q10"]).copy()
	q10_mean_df.insert(0, "question_no", "Q10")
	q10_mean_df.insert(1, "metric_type", "mean_weight")
	q10_mean_df.rename(columns={"stakeholder": "label", "mean_weight": "value"}, inplace=True)
	q10_mean_df["rate"] = pd.NA
	summary_tables.append(q10_mean_df[["question_no", "metric_type", "label", "value", "rate"]])

	q6_weighted_df = prepare_q6_weighted_score_table(q6_ranked_df).copy()
	q6_weighted_df.insert(0, "question_no", "Q6")
	q6_weighted_df.insert(1, "metric_type", "weighted_score")
	q6_weighted_df.rename(columns={"option": "label", "weighted_score": "value"}, inplace=True)
	q6_weighted_df["rate"] = pd.NA
	summary_tables.append(q6_weighted_df[["question_no", "metric_type", "label", "value", "rate"]])

	return pd.concat(summary_tables, ignore_index=True)


def generate_descriptive_summary(cleaned_df, multi_choice_binary_df, q6_ranked_df, question_column_mapping):
	summary_df = build_descriptive_summary(cleaned_df, multi_choice_binary_df, q6_ranked_df, question_column_mapping)
	output_path = OUTPUT_DIR / "descriptive_summary.csv"
	summary_df.to_csv(output_path, index=False, encoding="utf-8-sig")
	covered_questions = summary_df["question_no"].drop_duplicates().tolist()

	print()
	print("步骤7：生成图表统计汇总表")
	print(f"本步输入：{CLEANED_DATA_PATH}、{MULTI_CHOICE_BINARY_PATH}、{Q6_RANKED_PATH}")
	print("本步输出：output/descriptive_summary.csv")
	print("终端验收信号：打印 descriptive_summary.csv 已保存，并输出汇总表行数、包含的题号清单、保存路径")
	print("descriptive_summary.csv 已保存")
	print(f"- 汇总表行数 = {len(summary_df)}")
	print(f"- 包含的题号清单 = {covered_questions}")
	print(f"- 已保存 {output_path}")


def main():
	configure_matplotlib_fonts()
	cleaned_df = load_cleaned_data()
	question_column_mapping = build_question_column_mapping(cleaned_df)
	generate_single_choice_charts(cleaned_df, question_column_mapping)
	multi_choice_binary_df = load_multi_choice_binary_data()
	generate_multi_select_charts(multi_choice_binary_df)
	generate_q9_combined_chart(cleaned_df, question_column_mapping)
	generate_q10_mean_weight_chart(cleaned_df, question_column_mapping)
	q6_ranked_df = load_q6_ranked_data()
	generate_q6_weighted_score_chart(q6_ranked_df)
	generate_descriptive_summary(cleaned_df, multi_choice_binary_df, q6_ranked_df, question_column_mapping)


if __name__ == "__main__":
	main()