function toggleBookmark(itemData) {
    fetch('/api/bookmark', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(itemData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.action === 'removed') {
                // 북마크 페이지에서는 카드를 제거
                const card = document.querySelector(`[data-item-id="${itemData.item_id}"]`).closest('.product-card');
                card.remove();
                
                // 카드가 모두 제거되었는지 확인
                const remainingCards = document.querySelectorAll('.product-card');
                if (remainingCards.length === 0) {
                    location.reload(); // 빈 상태 메시지를 보여주기 위해 페이지 새로고침
                }
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('북마크 처리 중 오류가 발생했습니다.');
    });
}