import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage

# --- 1. 頁面配置與樣式 (前端美化) ---
st.set_page_config(
    page_title="毒雞湯大師 Pro",
    page_icon="😒",
    layout="centered",
    initial_sidebar_state="auto",
)

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

try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except KeyError:
    st.error("錯誤：找不到 OpenRouter API 金鑰。請在 Streamlit Cloud 的 Secrets 中設定。")
    st.stop()

llm = ChatOpenAI(
    model="deepseek/deepseek-v3-base:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    temperature=0.8
)

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

agent = create_tool_calling_agent(llm, tools=[], prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=[], verbose=True)


# --- 3. 聊天介面與狀態管理 ---

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "又怎麼了？說吧，我聽著呢。別浪費我太多時間。"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("說出你的煩惱..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("大師正在鄙視地看著你，並思考如何點醒你..."):
            
            # 【核心邏輯修復】我們只轉換「到上一句為止」的歷史紀錄
            # Python 的 [:-1] 語法可以取得列表中除了最後一項之外的所有元素
            chat_history_formatted = []
            for msg in st.session_state.messages[:-1]:
                if msg["role"] == "user":
                    chat_history_formatted.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    chat_history_formatted.append(AIMessage(content=msg["content"]))

            try:
                # 現在，chat_history 和 input 完美地分開了
                response = agent_executor.invoke({
                    "input": user_input,
                    "chat_history": chat_history_formatted
                })
                ai_response = response["output"]
            except Exception as e:
                ai_response = f"哎呀，出錯了，看來連我都救不了你。錯誤：{e}"

            st.markdown(ai_response)
    
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

with st.sidebar:
    st.header("操作")
    if st.button("清空對話紀錄", use_container_width=True, type="primary"):
        st.session_state.messages = [
            {"role": "assistant", "content": "哼，清空了煩惱就不存在了嗎？快說，又有什麼新麻煩了？"}
        ]
        st.rerun()