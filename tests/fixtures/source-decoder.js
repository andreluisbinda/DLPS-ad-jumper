
(function() {
    // Hàm giải mã base64 unicode an toàn
    function b64DecodeUnicode(str) {
        try {
            return decodeURIComponent(atob(str).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
        } catch(e) {
            return atob(str); // fallback nếu lỗi
        }
    }

    // Tìm và giải mã tất cả các phần tử secure-data
    document.querySelectorAll('.secure-data').forEach(function(div) {
        var payload = div.getAttribute('data-payload');
        if (payload) {
            div.innerHTML = b64DecodeUnicode(payload);
            // Xóa attribute để sạch source code (tùy chọn)
            div.removeAttribute('data-payload');
        }
    });

    // Optional: Chạy lại sau 1-2 giây nếu nội dung load chậm (ajax/lazy)
    setTimeout(function() {
        document.querySelectorAll('.secure-data').forEach(function(div) {
            var payload = div.getAttribute('data-payload');
            if (payload) {
                div.innerHTML = b64DecodeUnicode(payload);
                div.removeAttribute('data-payload');
            }
        });
    }, 2000);

})();
