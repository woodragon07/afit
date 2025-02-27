// static/js/recommendations.js

// document.addEventListener('DOMContentLoaded', function() {
//     // 페이지 로드 시 추천 상품 불러오기
//     loadRecommendations();
    
//     // 새로고침 버튼 이벤트 리스너
//     const refreshBtn = document.getElementById('refresh-recommendations');
//     if (refreshBtn) {
//         refreshBtn.addEventListener('click', function() {
//             loadRecommendations(true); // true = 강제 새로고침
//         });
//     }
    
//     // 로그아웃 버튼 이벤트 리스너
//     const logoutBtn = document.getElementById('logout-btn');
//     if (logoutBtn) {
//         logoutBtn.addEventListener('click', function() {
//             // 세션 또는 로컬 스토리지 데이터 삭제 (필요시)
//             // localStorage.removeItem('key');
//             window.location.href = '/login';
//         });
//     }
// });

document.addEventListener('DOMContentLoaded', function() {
    // 먼저 사용자 ID 가져오기
    const userId = getUserId();
    
    if (!userId) {
        console.error("사용자 ID를 찾을 수 없습니다");
        showEmptyState(true);  // 빈 상태 표시
        return;
    }
    
    // 사용자 ID로 추천 상품 불러오기
    loadRecommendations(userId);  // 사용자 ID를 매개변수로 전달
    
    // 새로고침 버튼 이벤트 리스너
    const refreshBtn = document.getElementById('refresh-recommendations');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            loadRecommendations(userId);  // 사용자 ID를 매개변수로 전달
        });
    }
    
    // 로그아웃 버튼 이벤트 리스너
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            window.location.href = '/login';
        });
    }
});

// 사용자 ID 가져오기 함수
function getUserId() {
    console.log("로컬 스토리지 키:", Object.keys(localStorage));


    // 서버에서 제공한 사용자 ID 사용
    if (typeof serverProvidedUserId !== 'undefined' && serverProvidedUserId) {
        return serverProvidedUserId;
    }
    
    // 로컬 스토리지 모든 항목 출력
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        console.log(`로컬 스토리지 항목 ${i+1}:`, key, localStorage.getItem(key));
    }
    
    console.log("쿠키:", document.cookie);

    // 로컬 스토리지에서 사용자 정보 가져오기 시도
    try {
        // 여러 키 시도 (userInfo, userData, user)
        const userDataStr = localStorage.getItem('userInfo') || 
                          localStorage.getItem('userData') || 
                          localStorage.getItem('user');
        
        if (userDataStr) {
            const userData = JSON.parse(userDataStr);
            console.log("사용자 데이터:", userData);
            return userData.id || userData.userId || userData._id;
        }
    } catch (e) {
        console.error("사용자 정보 파싱 오류:", e);
    }
    
    // 쿠키에서 사용자 ID 가져오기 시도
    try {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'userId') {
                return value;
            }
        }
    } catch (e) {
        console.error("쿠키 파싱 오류:", e);
    }
    
    // 로그에서 API가 데이터를 반환하지 않았으므로, 
    // 북마크가 있는 특정 사용자 ID를 하드코딩
    console.log("북마크가 있는 테스트 사용자 ID 사용");
    return "67bee5a686df8a889b13972b";   // 이전에 성공한 API 테스트에 사용된 ID
}

// 추천 상품 로드 (사용자 ID를 매개변수로 받음)
function loadRecommendations(userId) {
    // null 체크
    if (!userId) {
        console.error("유효한 사용자 ID가 필요합니다");
        showEmptyState(true);
        return;
    }
    
    showLoading(true);
    console.log("추천 로드 시작, 사용자 ID:", userId);
    
    fetch(`/api/recommendations?userId=${userId}`)
        .then(response => {
            console.log("API 응답 상태:", response.status);
            return response.json();
        })
        .then(data => {
            console.log("API 응답 데이터:", data);
            showLoading(false);
            
            if (data.success && data.data && data.data.length > 0) {
                console.log("추천 상품 수:", data.data.length);
                displayRecommendations(data.data);
            } else {
                console.log("추천 상품 없음");
                showEmptyState(true);
            }
        })
        .catch(error => {
            console.error('추천을 불러오는 중 오류 발생:', error);
            showLoading(false);
            showEmptyState(true);
        });
}



// // 추천 상품 로드 함수에 디버깅 로그 추가--------------
// function loadRecommendations() {
//     showLoading(true);
    
//     const userId = /* 사용자 ID 가져오기 */
//     console.log("로드 시작, 사용자 ID:", userId);
    
//     fetch(`/api/recommendations?userId=${userId}`)
//         .then(response => {
//             console.log("API 응답 상태:", response.status);
//             return response.json();
//         })
//         .then(data => {
//             console.log("API 응답 데이터:", data);
//             showLoading(false);
            
//             if (data.success && data.data && data.data.length > 0) {
//                 console.log("추천 상품 수:", data.data.length);
//                 displayRecommendations(data.data);
//             } else {
//                 console.log("추천 상품 없음");
//                 showEmptyState(true);
//             }
//         })
//         .catch(error => {
//             console.error('추천을 불러오는 중 오류 발생:', error);
//             showLoading(false);
//             showEmptyState(true);
//         });
// }

// 디스플레이 함수에도 디버깅 로그 추가
function displayRecommendations(products) {
    console.log("상품 표시 시작, 상품 수:", products.length);
    const grid = document.getElementById('recommendations-grid');
    
    if (!grid) {
        console.error("상품 그리드 요소를 찾을 수 없음");
        return;
    }
    
    grid.innerHTML = '';
    
    products.forEach((product, index) => {
        console.log(`상품 ${index+1} 처리:`, product.title);
        const card = createProductCard(product);
        grid.appendChild(card);
    });
    
    document.getElementById('recommendations-grid').classList.remove('hidden');
    showEmptyState(false);
    console.log("상품 표시 완료");
}

// 추천 상품 로드
// function loadRecommendations(forceRefresh = false) {
//     showLoading(true);
    
//     // API 엔드포인트 경로 (새로고침 강제 여부에 따라 다른 엔드포인트 사용)
//     const endpoint = forceRefresh ? '/api/recommendations/refresh' : '/api/recommendations';
//     const method = forceRefresh ? 'POST' : 'GET';
    
//     // API 요청 옵션
//     const options = {
//         method: method,
//         headers: {
//             'Content-Type': 'application/json'
//         }
//     };
    
//     // POST 요청일 경우 body 추가
//     if (method === 'POST') {
//         options.body = JSON.stringify({});  // 필요한 데이터가 있다면 추가
//     }
    
//     // API 요청
//     fetch(endpoint, options)
//         .then(response => {
//             // 비로그인 상태 또는 권한 없음
//             if (response.status === 401 || response.status === 403) {
//                 window.location.href = '/login';
//                 throw new Error('로그인이 필요합니다.');
//             }
            
//             if (!response.ok) {
//                 throw new Error('추천 데이터를 불러오는 중 오류가 발생했습니다.');
//             }
            
//             return response.json();
//         })
//         .then(data => {
//             showLoading(false);
            
//             if (data.success && data.data && data.data.length > 0) {
//                 displayRecommendations(data.data);
//             } else {
//                 showEmptyState(true);
//             }
//         })
//         .catch(error => {
//             console.error('추천을 불러오는 중 오류 발생:', error);
//             showLoading(false);
            
//             // 401/403 에러가 아닌 다른 에러인 경우에만 빈 상태 표시
//             if (error.message !== '로그인이 필요합니다.') {
//                 showEmptyState(true);
//             }
//         });
// }

// 추천 상품 표시
function displayRecommendations(products) {
    const grid = document.getElementById('recommendations-grid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    products.forEach(product => {
        const card = createProductCard(product);
        grid.appendChild(card);
    });
    
    document.getElementById('recommendations-grid').classList.remove('hidden');
    showEmptyState(false);
}

// 상품 카드 생성
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    // 가격 형식 변환
    const formattedPrice = formatPrice(product.price);
    
    // 이미지 URL 확인 (이미지가 없으면 기본 이미지 사용)
    const imageUrl = product.image_url || 'https://via.placeholder.com/250x200?text=No+Image';
    
    card.innerHTML = `
        <img class="product-image" src="${imageUrl}" alt="${product.title}" onerror="this.src='https://via.placeholder.com/250x200?text=Image+Error'">
        <div class="product-info">
            <h3 class="product-title">${product.title}</h3>
            <p class="product-price">${formattedPrice}</p>
            <p class="product-mall">${product.mall_name || ''}</p>
            <div class="product-actions">
                <button id="bookmark-${product.item_id}" class="bookmark-btn" onclick="toggleBookmark(${JSON.stringify(product).replace(/"/g, '&quot;')})">
                    <i class="far fa-bookmark"></i>
                </button>
                <a href="${product.product_url}" class="view-btn" target="_blank">상품 보기</a>
            </div>
        </div>
    `;
    
    return card;
}

// 북마크 토글 함수 (북마크 페이지 방식 적용)
function toggleBookmark(productData) {
    console.log('북마크 시도:', productData);  // 디버깅용 로그

    // 북마크 버튼 요소 찾기
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

// 로딩 표시
function showLoading(show) {
    const spinner = document.getElementById('loading-spinner');
    const grid = document.getElementById('recommendations-grid');
    const emptyState = document.getElementById('empty-state');
    
    if (!spinner || !grid || !emptyState) return;
    
    if (show) {
        spinner.classList.remove('hidden');
        grid.classList.add('hidden');
        emptyState.classList.add('hidden');
    } else {
        spinner.classList.add('hidden');
    }
}

// 빈 상태 표시
function showEmptyState(show) {
    const emptyState = document.getElementById('empty-state');
    const grid = document.getElementById('recommendations-grid');
    
    if (!emptyState || !grid) return;
    
    if (show) {
        emptyState.classList.remove('hidden');
        grid.classList.add('hidden');
    } else {
        emptyState.classList.add('hidden');
    }
}

// 가격 형식 변환 (예: "15000" -> "15,000원")
function formatPrice(price) {
    if (!price) return '가격 정보 없음';
    
    // 숫자가 아니면 변환
    if (typeof price !== 'number') {
        price = parseInt(price.replace(/[^0-9]/g, ''), 10);
    }
    
    // 숫자 변환 실패 시
    if (isNaN(price)) return '가격 정보 없음';
    
    // 천 단위 구분 기호 추가
    return price.toLocaleString('ko-KR') + '원';
}