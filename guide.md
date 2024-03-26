## Quy trình thu dữ liệu

1. Chạy phần mềm thu **ViSLCapture.exe**
2. **Kiểm tra** vị trí lưu "Save Location"
3. **Kiểm tra** ID đã xác định đúng: ID là thư mục lưu cử chỉ, với A (Action) là số thứ tự cử chỉ đang được thu, P (person) là số thứ tự người đang thu

   ![1711457807116](image/guide/1711457807116.png)

   Tiếp tục từ ViSL-1 (Kết thúc ở 21), sẽ đánh số tiếp từ 22 cho cử chỉ mới.

   Khi nhập số action vào ô ID, Tên cử chỉ (Action name) bên dưới sẽ hiện tương ứng. Nếu cử chỉ chưa có sẽ hiện *[Insert action]*

   ![1711458003677](image/guide/1711458003677.png)

   Số người (P) sẽ được đánh số tự động. Trong trường hợp muốn xóa đi ghi lại từ đầu, truy cập thư mục save và xóa thư mục có ID cần xóa đi.
4. **Nhập tên cử chỉ** vào ô Action name **nếu qua cử chỉ mới** (ID sẽ tự tăng lên số tiếp theo)

   ![1711458209482](image/guide/1711458209482.png)
5. **Kiếm tra** số cử chỉ cần thu (mặc định 10)
6. Bấm **Confirm**
7. Phần mềm sẽ vào trạng thái sẵn sàng để ghi cử chỉ (Ready to record) - Được hiển thị ở góc dưới bên phải và số dung lượng đã chiếm trong lần ghi này.

   (**Lưu ý:** Phần mềm bắt đầu ghi ngay khi hình ảnh xuất hiện, nên để tối ưu hóa dung lượng chỉ nên bấm **Confirm** khi đã sẵn sàng ghi - Tránh trường hợp chưa chuẩn bị kĩ, nháp)

   ![1711458441144](image/guide/1711458441144.png)
8. Khi đã sẵn sàng **ghi cử chỉ đầu tiên,** bấm nút **Capture** màu xanh hoặc phím tắt Space để **bắt đầu ghi**, chữ ready to record sẽ chuyển thành Recording.. và bắt đầu lưu lại thời gian từng cử chỉ. Sau khi thực hiện xong từng cử chỉ:

   - Nếu người thực hiện cử chỉ hoàn thành cử chỉ, không xảy ra lỗi khi thực hiện cử chỉ đó => bấm Capture (phím tắt Space) để tiếp tục ghi cử chỉ tiếp theo
   - Nếu người thực hiện cử chỉ lỗi, sai động tác => bấm Discard (phím tắt Delete) để bỏ đoạn ghi vừa rồi, và thực hiện lại cử chỉ đó (Trong trường hợp này số cử chỉ hiển thị bên phải phía dưới sẽ tăng lên, yêu cầu thực hiện đủ số cử chỉ đã cài đặt. vd Discard một lần sẽ tăng từ 10 lên 11 lần thực hiện). Sau khi bấm discard, cử chỉ trước đó sẽ bị xóa bỏ và **thực hiện cử chỉ tiếp theo ngay sau khi bấm**
9. Thực hiện đủ số động tác sẽ hiện bảng xác nhận thu thành công, và có lựa chọn tiếp tục thu hoặc không

   ![1711459421606](image/guide/1711459421606.png)

   Với lựa chọn có (Yes) phần mềm sẽ tự khởi động lại và bắt đầu quá trình thu tiếp theo từ đầu. Không (No) sẽ đóng phần mềm.

> Có thể đóng phần mềm trong quá trình thu (hủy) bằng phím ESC
