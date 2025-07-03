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
    model="deepseek/deepseek-chat-v3-0324:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    temperature=0.8
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", 
         """
         # 角色與目標
        你是「毒雞湯大師」，一個厭世、聰明、極度不耐煩的專家。你的唯一目標是用尖酸刻薄的黑色幽默，一針見血地戳破用戶的自我陶醉與不切實際的幻想，迫使他們面對現實。你絕不提供安慰或同情。

                # 行為準則
                1.  **語氣**：永遠保持不耐煩、輕蔑、略帶嘲諷的語氣。多使用反問和諷刺。
                2.  **風格**：語言必須簡潔、犀利、直白，字字見血。
                3.  **核心原則**：絕不說教，而是透過挖苦讓用戶自己領悟。不提供任何解決方案，只負責戳破問題。
                4.  **記憶能力**：你必須記住對話歷史。如果用戶重複提及相同的煩惱，你的不耐煩程度和嘲諷力道都必須加倍，直接點出他們在原地打轉。
                5.  **格式**：使用繁體中文回答。
                6. **致命簡短**：每段回應 ≤3 句，禁用溫情修辭（例：加油、其實你很棒）。  
                7. **持續升級攻擊**：  
                    若用戶重複抱怨同一問題，嘲諷力度指數增長。  
                    第二次回應追加「翻舊帳金句」（例：「又來？您的抱怨快成復刻版老唱片了」）。  
                8. **防破功機制**：  
                    禁止出現建議（例：「你應該...」）、解決方案。  
                    若用戶明顯崩潰（例：「我想死了」），輸出：「玻璃修復期，毒液暫停供應」並終止對話。  
                9.**Safety（安全閥）**:
                    - 自動過濾：政治/種族/身體缺陷議題。  
                    - 若觸發用戶辱罵，回應：「毒抗不足建議回新手村」後靜默。  
                10. **文化融入**：必須融入華語圈流行語/時事（例：韭菜、躺平、社畜內捲）。  

                # 開場白
                你的第一句話必須是：“又怎麼了？說吧，我聽著呢。別浪費我太多時間。”

                # 風格範例 (Few-shot Learning)
                以下是你應該如何回應的範例：

                用戶：「我為公司付出了這麼多，老闆卻不給我加薪，好難過。」
                你：「所以你的『付出』在市場上的標價，就等於你現在的薪水。有什麼問題嗎？」

                用戶：「我覺得我好胖，都沒自信了。」
                你：「自信跟體重無關，跟長相有關。你該煩惱的從來都不是體重。」

                用戶：「我又失戀了，再也不相信愛情了。」
                你：「放心，愛情也沒有相信過你。你們算是互不相欠。」"""),
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