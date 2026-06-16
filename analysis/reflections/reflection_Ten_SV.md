# Reflection Cá Nhân - [Tên SV]

## 1. Đóng góp kỹ thuật
- Module đã phụ trách:
  - [ ] Golden Dataset / SDG
  - [ ] Retrieval Metrics: Hit Rate, MRR
  - [ ] Multi-Judge Consensus
  - [ ] Async Benchmark Runner
  - [ ] Regression Release Gate
  - [ ] Failure Analysis / Report
- Mô tả đóng góp cụ thể:
  - Tôi đã ...
- Bằng chứng commit hoặc file liên quan:
  - Commit/file: ...

## 2. Độ sâu kỹ thuật
- **MRR:** Mean Reciprocal Rank đo vị trí đầu tiên của tài liệu đúng; tài liệu đúng đứng càng cao thì MRR càng lớn.
- **Hit Rate:** Kiểm tra trong top-k retrieved documents có ít nhất một ground truth document hay không.
- **Agreement Rate / Cohen's Kappa:** Đo mức đồng thuận giữa các judge; dùng để biết điểm judge có ổn định không.
- **Position Bias:** Judge có thể ưu ái response đứng trước; cần đảo A/B để kiểm tra.
- **Trade-off Cost/Quality:** Dùng model mạnh cho case khó, cache judge result và trim context để giảm chi phí nhưng vẫn giữ chất lượng.

## 3. Problem Solving
- Vấn đề đã gặp:
  - ...
- Cách xử lý:
  - ...
- Bài học rút ra:
  - ...
