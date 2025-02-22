let currentMode = "helper"; // 현재 선택된 모드 추적

function goSearch(){
  const val = document.getElementById("landingInput").value.trim();
  if(!val) return;
  // 현재 선택된 모드와 함께 URL 전달
  window.location.href = "/search?query=" + encodeURIComponent(val) + "&mode=" + currentMode;
}

// 탭 클릭 시 색상 전환 및 모드 변경
const tabBtns = document.querySelectorAll(".tab-btn");
tabBtns.forEach(btn=>{
  btn.addEventListener("click",()=>{
    // 모드 업데이트
    currentMode = btn.dataset.tab;
    
    // 버튼 스타일 업데이트
    tabBtns.forEach(b=>{
      b.classList.remove("tab-active");
      b.classList.add("tab-inactive");
    });
    btn.classList.remove("tab-inactive");
    btn.classList.add("tab-active");
  });
});

//한/영 페이지 변환 기능능
const languageSelect = document.getElementById('languageSelect');
        
        languageSelect.addEventListener('change', function() {
            const selectedLanguage = this.value;
            if (selectedLanguage === 'en') {
                window.location.href = '/english'; //영어로로
            } else {
                window.location.href = '/'; //한글로
            }
        });

// // 영어로 바꾸면 영어페이지 검색으로 돌아감
// document.addEventListener("DOMContentLoaded", function() {
//   const languageSelect = document.getElementById("languageSelect");

//   if (languageSelect) {
//       languageSelect.addEventListener("change", function() {
//           const selectedLanguage = this.value;
//           if (selectedLanguage === "en") {
//               window.location.href = "/english"; // 영어 페이지로 이동
//           } else {
//               window.location.href = "/"; // 한글 페이지로 이동
//           }
//       });
//   } else {
//       console.error("languageSelect 요소를 찾을 수 없습니다.");
//   }
// });

