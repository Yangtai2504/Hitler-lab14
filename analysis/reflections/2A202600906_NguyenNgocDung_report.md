
# Báo cáo phản ánh cá nhân — Retrieval & SDG (Data Team)

* **Họ và tên:** Nguyễn Ngọc Dũng
* **Vai trò:** Data Engineer / Retrieval Specialist
* **Module:** Retrieval & Synthetic Data Generation (SDG)
* **Sprint:** Lab Day 14

---

# 1. Tóm tắt đóng góp

Trong sprint này, tôi phụ trách xây dựng pipeline tạo dữ liệu tổng hợp (Synthetic Data Generation - SDG) và đánh giá hiệu quả của mô hình truy xuất (Retrieval). Các công việc chính bao gồm:

* Xây dựng chương trình sinh dữ liệu tổng hợp để tạo bộ dữ liệu phục vụ đánh giá Retrieval.
* Xây dựng bộ đánh giá Retrieval sử dụng TF-IDF làm mô hình baseline.
* Tự động hóa quá trình chạy thử và sinh báo cáo kết quả.

---

# 2. Nội dung thực hiện

## 2.1. Xây dựng Synthetic Data Generation (SDG)

Tôi phát triển file `data/synthetic_gen.py` với mục tiêu tạo một **Golden Dataset** có thể tái tạo và sử dụng trong các lần đánh giá sau.

Kết quả tạo được gồm:

* **80 tài liệu tổng hợp** lưu trong thư mục:

<pre class="overflow-visible! px-0!" data-start="957" data-end="975"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>data/docs/</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

* **60 bộ câu hỏi kiểm thử** lưu tại:

<pre class="overflow-visible! px-0!" data-start="1016" data-end="1045"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>data/golden_set.jsonl</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

Mỗi test case bao gồm:

* `id`
* `question`
* `expected_answer`
* `ground_truth_doc_ids`

để xác định chính xác tài liệu chứa đáp án đúng.

---

## 2.2. Thiết kế dữ liệu

Dữ liệu được sinh từ một tập chủ đề nhỏ nhưng được biến đổi theo nhiều cách nhằm mô phỏng dữ liệu thực tế.

Để tăng độ khó của bài toán Retrieval, cứ mỗi 10 tài liệu tôi chèn thêm các câu gây nhiễu (distractor sentences), khiến nhiều tài liệu có nội dung tương tự nhau.

Ngoài ra:

* khoảng **15%** test case được thiết kế theo dạng  **adversarial** , bao gồm:
* nhiều tài liệu cùng chứa đáp án đúng;
* câu hỏi được diễn đạt lại (paraphrase);
* nhiều ground truth cho cùng một câu hỏi.

Điều này giúp đánh giá khả năng Retrieval trong các tình huống khó thay vì chỉ kiểm tra các trường hợp đơn giản.

---

## 2.3. Xây dựng Retrieval Evaluation

Tôi xây dựng file:

<pre class="overflow-visible! px-0!" data-start="1887" data-end="1919"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>engine/retrieval_eval.py</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

để đánh giá chất lượng Retrieval.

Mô hình Retrieval sử dụng:

* TF-IDF
* `ngram_range=(1,2)`
* loại bỏ English stop words.

Lựa chọn TF-IDF giúp:

* không phụ thuộc Vector Database;
* dễ tái lập kết quả;
* chạy nhanh trong môi trường CI;
* làm baseline trước khi triển khai Retrieval bằng Embedding.

Kết quả đánh giá được lưu tại:

<pre class="overflow-visible! px-0!" data-start="2255" data-end="2293"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>reports/retrieval_metrics.json</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

---

## 2.4. Tự động hóa

Để người khác có thể tái tạo toàn bộ quy trình dễ dàng, tôi bổ sung:

<pre class="overflow-visible! px-0!" data-start="2391" data-end="2423"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>scripts/run_retrieval.py</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

Quá trình chạy chỉ cần:

<pre class="overflow-visible! px-0!" data-start="2450" data-end="2556"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="relative h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class=""><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>pip install </span><span class="ͼ12">-r</span><span> requirements.txt</span><br/><br/><span>python data/synthetic_gen.py</span><br/><br/><span>python scripts/run_retrieval.py</span></code></pre></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></div></div></pre>

---

# 3. Chỉ số đánh giá

Hai chỉ số chính được sử dụng gồm:

## Hit Rate (Top-k)

Đánh giá xem trong Top-k tài liệu được truy xuất có xuất hiện ít nhất một tài liệu đúng hay không.

Nếu có:

<pre class="overflow-visible! px-0!" data-start="2751" data-end="2766"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>Hit = 1</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

Ngược lại:

<pre class="overflow-visible! px-0!" data-start="2780" data-end="2795"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>Hit = 0</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

---

## Mean Reciprocal Rank (MRR)

MRR được tính bằng nghịch đảo của vị trí tài liệu đúng đầu tiên trong danh sách Retrieval.

Nếu không tìm thấy tài liệu đúng:

<pre class="overflow-visible! px-0!" data-start="2960" data-end="2975"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>MRR = 0</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

Chỉ số này phản ánh mức độ Retrieval đưa tài liệu đúng lên đầu danh sách.

---

# 4. Kết quả

Sau khi chạy trên bộ dữ liệu tổng hợp:

* **Average Hit Rate (Top-5):** **0.5833**
* **Average MRR:** **0.3525**

Các file sinh ra:

* `data/golden_set.jsonl`
* `data/docs/*.txt`
* `reports/retrieval_metrics.json`

---

# 5. Đóng góp kỹ thuật

Các file được xây dựng gồm:

* `data/synthetic_gen.py`
* `engine/retrieval_eval.py`
* `scripts/run_retrieval.py`
* `requirements.txt`

Những thành phần này giúp nhóm có một pipeline hoàn chỉnh để:

* sinh dữ liệu đánh giá;
* xây dựng bộ Retrieval baseline;
* đánh giá hiệu quả Retrieval;
* tái lập kết quả một cách tự động.

---

# 6. Khó khăn và hướng giải quyết

### Khó khăn 1

Cần xây dựng một hệ thống Retrieval đơn giản, chạy nhanh và không phụ thuộc vào Vector Database.

**Giải pháp**

Sử dụng TF-IDF kết hợp n-gram để tạo baseline có tính xác định (deterministic), phù hợp cho việc kiểm thử và tích hợp CI.

---

### Khó khăn 2

Khó tạo ra các trường hợp kiểm thử phản ánh đúng độ khó của dữ liệu thực tế.

**Giải pháp**

Thiết kế các test case adversarial bằng cách:

* thêm nhiều ground truth;
* diễn đạt lại câu hỏi;
* chèn các câu gây nhiễu giữa các tài liệu.

Qua đó giúp đánh giá Retrieval sát với các tình huống thực tế hơn.

---

# 7. Bài học rút ra

Trong quá trình thực hiện, tôi nhận thấy:

* Chất lượng của dữ liệu tổng hợp ảnh hưởng trực tiếp đến khả năng đánh giá Retrieval.
* Việc bổ sung các tài liệu gây nhiễu giúp bộc lộ rõ những điểm yếu của hệ thống Retrieval.
* Mặc dù TF-IDF là một phương pháp truyền thống, nhưng vẫn rất hữu ích để xây dựng baseline trước khi chuyển sang các mô hình Embedding hiện đại.
* Một quy trình có khả năng tái lập và tự động hóa sẽ giúp việc đánh giá và so sánh giữa các phiên bản hệ thống trở nên thuận tiện hơn.

---

# 8. Định hướng phát triển

Trong các giai đoạn tiếp theo, tôi đề xuất:

* Mở rộng bộ đánh giá để hỗ trợ Retrieval bằng Embedding kết hợp các thư viện như FAISS hoặc Annoy.
* So sánh giữa chi phí tính toán và chất lượng Retrieval của các phương pháp khác nhau.
* Theo dõi thêm số lượng token và chi phí trong quá trình Retrieval và Generation để phục vụ đánh giá hiệu năng.
* Mở rộng số lượng test case khó và bổ sung một tập dữ liệu được kiểm chứng thủ công nhằm nâng cao độ tin cậy của bộ đánh giá.

---

# 9. Tự đánh giá

Qua sprint này, tôi đã cải thiện khả năng:

* thiết kế hệ thống Retrieval theo hướng có thể mở rộng;
* xây dựng pipeline sinh dữ liệu và đánh giá một cách tự động;
* phát triển các công cụ hỗ trợ kiểm thử có khả năng tái lập kết quả;
* hiểu rõ hơn mối liên hệ giữa chất lượng dữ liệu SDG, hiệu quả Retrieval và chất lượng của hệ thống RAG trong toàn bộ pipeline.
