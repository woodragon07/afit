
const chatBox = document.getElementById("chat-box");
const chatInput = document.getElementById("chat-input");
const productArea = document.getElementById("product-area");
const sendButton = document.getElementById("send-button");
let currentMode = "helper"; // 기본값 설정

// URL 파라미터 처리
const urlParams = new URLSearchParams(window.location.search);
const initialQuery = urlParams.get("query");
const initialMode = urlParams.get("mode") || "helper";

// 초기 모드 설정
document.querySelectorAll('.tab-button').forEach(btn => {
    if (btn.dataset.tab === initialMode) {
        btn.classList.add('tab-active');
        btn.classList.remove('tab-inactive');
        currentMode = initialMode;

    } else {
        btn.classList.remove('tab-active');
        btn.classList.add('tab-inactive');
    }
});

// 첫 메시지 처리
if(initialQuery){
    addUserMessage(initialQuery);
    fetchMessage(initialQuery);
}

// 엔터
chatInput.addEventListener("keypress",(e)=>{
  if(e.key==="Enter" && !e.shiftKey){
    e.preventDefault();
    sendMessage();
  }
});
sendButton.addEventListener("click", sendMessage);

function sendMessage(){
  const userMsg = chatInput.value.trim();
  if(!userMsg) return;
  chatInput.value="";
  addUserMessage(userMsg);
  fetchMessage(userMsg);
}

async function fetchMessage(message){
  try {
    const res = await fetch("/chat", {
      method:"POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ 
        message,
        mode: currentMode
      })
    });
    const data = await res.json();
    
    // 상품 영역 초기화
    productArea.innerHTML = "";
    // 모드에 따른 클래스 설정
    productArea.className = currentMode === "shopping" ? "shopping-secretary-grid" : "product-grid";
    
    data.forEach(item=>{
      if(item.html){
        productArea.innerHTML += item.response;
      } else {
        addBotMessage(item.response);
      }
    });
    chatBox.scrollTop = chatBox.scrollHeight;
  } catch(err){
    console.error(err);
    addBotMessage("오류가 발생했습니다.");
  }
}

function addUserMessage(msg){
  const div = document.createElement("div");
  div.classList.add("user-message");
  div.textContent = msg;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function addBotMessage(msg){
  const div = document.createElement("div");
  div.classList.add("bot-message");
  div.textContent = msg;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function showModeChangeMessage(mode) {
    const modeNames = {
        "helper": "도우미",
        "shopping": "쇼핑비서"
    };
    
    const modeName = modeNames[mode] || mode;
    addBotMessage(`${modeName} 모드로 전환되었습니다.`);
    
    if (mode === "shopping") {
        addBotMessage("필요한 품목과 예산을 알려주세요. (예: 김치찌개 재료 준비, 캠핑용품 5만원 이내)");
    } else if (mode === "helper") {
        addBotMessage("찾으시는 상품을 알려주세요.");
    }
}

// showModeChangeMessage 함수는 삭제 (탭 버튼 이벤트에서 직접 처리하기 때문)

document.querySelectorAll(".tab-button").forEach(btn => {
btn.addEventListener("click", () => {
    const newMode = btn.dataset.tab;
    if (newMode === currentMode) return;

    // 버튼 스타일 업데이트
    document.querySelectorAll(".tab-button").forEach(b => {
        b.classList.remove("tab-active");
        b.classList.add("tab-inactive");
    });
    btn.classList.remove("tab-inactive");
    btn.classList.add("tab-active");

    // 모드 변경
    currentMode = newMode;

    // ⭐ 상품 UI가 깨지는 문제 해결 ⭐
    const productContainer = document.getElementById("product-container");
    if (productContainer) {
        if (currentMode === "shopping") {
            productContainer.classList.remove("product-grid");
            productContainer.classList.add("shopping-secretary-grid");
        } else {
            productContainer.classList.remove("shopping-secretary-grid");
            productContainer.classList.add("product-grid");
        }
    }

    // 모드 변경 메시지 출력
    showModeChangeMessage(currentMode);

    chatBox.scrollTop = chatBox.scrollHeight;
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