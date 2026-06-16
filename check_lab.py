import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def validate_lab() -> None:
    print("Đang kiểm tra định dạng bài nộp...")

    required_files = [
        "reports/summary.json",
        "reports/benchmark_results.json",
        "analysis/failure_analysis.md",
    ]

    missing = []
    for file_path in required_files:
        if (ROOT / file_path).exists():
            print(f"Tìm thấy: {file_path}")
        else:
            print(f"Thiếu file: {file_path}")
            missing.append(file_path)

    if missing:
        print(f"\nThiếu {len(missing)} file. Hãy bổ sung trước khi nộp bài.")
        return

    try:
        summary = json.loads((ROOT / "reports/summary.json").read_text(encoding="utf-8"))
        benchmark_results = json.loads((ROOT / "reports/benchmark_results.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"File JSON không hợp lệ: {exc}")
        return

    if "metrics" not in summary or "metadata" not in summary:
        print("summary.json thiếu trường metrics hoặc metadata.")
        return

    metrics = summary["metrics"]
    expected_metric_keys = [
        "avg_score",
        "hit_rate",
        "mrr",
        "faithfulness",
        "relevancy",
        "agreement_rate",
        "total_cost_usd",
        "p95_latency",
    ]
    missing_metrics = [key for key in expected_metric_keys if key not in metrics]
    if missing_metrics:
        print(f"Thiếu metrics: {missing_metrics}")
        return

    if len(benchmark_results) < 50:
        print(f"Golden benchmark cần 50+ cases, hiện có {len(benchmark_results)}.")
        return

    has_release_gate = "release_gate" in summary and "decision" in summary["release_gate"]
    reflection_dir = ROOT / "analysis" / "reflections"
    reflection_files = list(reflection_dir.glob("reflection_*.md")) if reflection_dir.exists() else []

    print("\n--- Thống kê nhanh ---")
    print(f"Tổng số cases: {summary['metadata'].get('total', 'N/A')}")
    print(f"Điểm trung bình: {metrics['avg_score']:.2f}")
    print(f"Hit Rate: {metrics['hit_rate'] * 100:.1f}%")
    print(f"MRR: {metrics['mrr']:.2f}")
    print(f"Agreement Rate: {metrics['agreement_rate'] * 100:.1f}%")
    print(f"Total Cost: ${metrics['total_cost_usd']}")
    print(f"P95 Latency: {metrics['p95_latency']}s")

    if has_release_gate:
        print(f"Release Gate: {summary['release_gate']['decision']}")
    else:
        print("CẢNH BÁO: Thiếu release_gate trong summary.json.")

    if reflection_files:
        print(f"Tìm thấy {len(reflection_files)} reflection cá nhân mẫu/thật.")
    else:
        print("CẢNH BÁO: Chưa có analysis/reflections/reflection_[Ten_SV].md.")

    if os.path.exists(ROOT / ".env"):
        print("Lưu ý: Có file .env cục bộ. Đảm bảo file này không được push lên GitHub.")

    print("\nBài lab đã sẵn sàng để chấm điểm tự động.")


if __name__ == "__main__":
    validate_lab()
