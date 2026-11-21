# @Thangvipsv4 --- Phản tư cá nhân

-   **Tôi đã làm (kèm link commit):**

    -   Phase 1: Xây dựng tài liệu QA, verification, proof và kiểm tra
        team.
    -   Phase 2: Triển khai Day Mode, Shop, Pause (simulation) và kiểm
        thử.
    -   Phase 3: Phát triển Inventory Adapter, schema kho cá thể,
        freshness, ID allocator và regression QA.
    -   Phase 4: Triển khai Soak runner, Contract v1.3, regression
        P1--P3, verification và proof.
    -   Commit Phase 4:
        [7af2b54](https://github.com/Thangvipsv4/K5-L3B-LAB-Day12-AI-SDLC-HNTT/commit/7af2b54f5cddc990a88926bdfb7a1bd73bbfc4bf).

-   **Tôi đã review (kèm link):** Kiểm tra Contract, kết quả Soak,
    regression tests và bằng chứng kiểm thử qua [commit Phase
    4](https://github.com/Thangvipsv4/K5-L3B-LAB-Day12-AI-SDLC-HNTT/commit/7af2b54f5cddc990a88926bdfb7a1bd73bbfc4bf).

-   **AI sai ở đâu và tôi phát hiện thế nào:** Benchmark không chạy
    thành công vì Chrome không trả kết quả sau 93 giây. Tôi kiểm tra
    artifact và xác nhận không có `bench.json`, nên ghi nhận trạng thái
    BLOCKED thay vì báo cáo hoàn thành.

-   **Điều tôi học được:** Hiểu hơn về quy trình phát triển phần mềm
    theo phase, làm việc với Git, tích hợp module, viết test, kiểm tra
    Contract và sử dụng AI hỗ trợ lập trình. Quan trọng nhất là phải tự
    xác minh kết quả AI bằng test và bằng chứng thực tế.
