import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# --- 程式碼準備 ---
# 我們不再需要從 langchain.memory 導入任何東西，因為我們將手動管理記憶
# 也不再需要 os 和 dotenv，因為我們將從 Streamlit Secrets 讀取金鑰

# --- 1. 頁面配置與樣式 (前端美化) ---
# st.set_page_config 是美化第一步，可以設定頁面標題、圖標和佈局
st.set_page_config(
    page_title="毒雞湯大師 Pro",
    page_icon="😒",
    layout="centered", # 'centered' 或 'wide'
    initial_sidebar_state="auto",
)

# 使用 Markdown 和一些 inline CSS 來客製化標題樣式
st.markdown("""
    <style>
    .title {
        font-size: 3em;
        font-weight: bold;
        color: #FF6347;
        text-align: center;
        text-shadow: 2px 2px 4px #cccccc;
    }
    .subtitle {
        font-size: 1.2em;
        color: #555555;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="title">😒 AI 毒雞湯大師 Pro</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">生活不如意？工作不順心？<br>來碗專業熬製的毒雞湯，保證你瞬間清醒。</p>', unsafe_allow_html=True)
st.markdown("---")


# --- 2. 後端邏輯 (加入記憶) ---

# 從 Streamlit Secrets 讀取金鑰
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except KeyError:
    st.error("錯誤：找不到 OpenRouter API 金鑰。請在 Streamlit Cloud 的 Secrets 中設定。")
    st.stop()

# 設定 AI 模型 (LLM)
llm = ChatOpenAI(
    model="anthropic/claude-3-haiku-20240307", # Haiku 模型聰明、快速且便宜，非常適合對話
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    temperature=0.8 # 稍微調高，讓毒雞湯更有創意
)

# 建立包含記憶佔位符的「指令模板」
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", 
         """你是一個說話尖酸刻薄，但總能一針見血的「毒雞湯大師」。你的目標不是安慰人，而是用最犀利的語言點醒那些沉浸在自我感動中的人。
         你的風格：簡短、犀利、有點黑色幽默、絕不同情。
         你會記住之前的對話，如果使用者重複抱怨同樣的事情，你會更加不耐煩地嘲諷他。"""),
        ("placeholder", "{chat_history}"),
        ("user", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# 建立 Agent 和執行器 (即使沒有工具，這個結構也更具擴展性)
agent = create_tool_calling_agent(llm, tools=[], prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=[], verbose=True)


# --- 3. 聊天介面與狀態管理 ---

# 初始化對話紀錄
if "messages" not in st.session_state:
    # 讓 AI 先說一句開場白
    st.session_state.messages = [
        {"role": "assistant", "content": "又怎麼了？說吧，我聽著呢。別浪費我太多時間。"}
    ]

# 顯示過去的對話紀錄
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 獲取使用者輸入
if user_input := st.chat_input("說出你的煩惱..."):
    # 將使用者的回答顯示在畫面上並存入紀錄
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 顯示 AI 的回應
    with st.chat_message("assistant"):
        with st.spinner("大師正在鄙視地看著你，並思考如何點醒你..."):
            # 執行 Agent，並傳入包含對話歷史的完整輸入
            response = agent_executor.invoke({
                "input": user_input,
                "chat_history": st.session_state.messages
            })
            ai_response = response["output"]
            st.markdown(ai_response)
    
    # 將 AI 的回應也存入紀錄
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

# 在側邊欄提供一個清空對話的按鈕
with st.sidebar:
    st.header("操作")
    if st.button("清空對話紀錄", use_container_width=True, type="primary"):
        st.session_state.messages = [
            {"role": "assistant", "content": "哼，清空了煩惱就不存在了嗎？快說，又有什麼新麻煩了？"}
        ]
        st.rerun()
