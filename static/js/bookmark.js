function toggleBookmark(productData) {
    console.log('북마크 시도:', productData);  // 디버깅용 로그

    const bookmarkBtn = document.getElementById(`bookmark-${productData.item_id}`);

    fetch('/api/bookmarks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(productData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`로그인 후 사용해주세요! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('서버 응답:', data);  // 디버깅용 로그
        
        if (data.success) {
            // 북마크 버튼 스타일 토글
            if (bookmarkBtn) {
                bookmarkBtn.classList.toggle('bookmarked');
            }
            // 성공 메시지 표시
            alert(data.message);
        } else {
            throw new Error(data.message || '북마크 처리 중 오류가 발생했습니다.');
        }
    })
    .catch(error => {
        console.error('북마크 오류:', error);
        alert(error.message);
    });
}

// ✅ 북마크 삭제 기능 추가
async function deleteBookmark(itemId) {
    if (!confirm("이 북마크를 삭제하시겠습니까?")) {
        return;
    }

    try {
        const response = await fetch(`/api/bookmarks/${itemId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        if (result.success) {
            // HTML에서 해당 북마크 카드 삭제
            const bookmarkCard = document.querySelector(`[data-bookmark-id="${itemId}"]`);
            if (bookmarkCard) {
                bookmarkCard.remove();
            }
        } else {
            alert(result.message || "북마크를 삭제할 수 없습니다.");
        }
    } catch (error) {
        console.error("북마크 삭제 오류:", error);
        alert("삭제 중 오류가 발생했습니다.");
    }
}
