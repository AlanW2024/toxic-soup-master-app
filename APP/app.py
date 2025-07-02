import streamlit as st
from openai import OpenAI
# import os # 這兩行不再需要
# from dotenv import load_dotenv

# --- 環境設定 ---
# 直接從 Streamlit 的 Secrets 功能讀取金鑰
api_key = st.secrets["OPENROUTER_API_KEY"]

# 檢查 API 金鑰是否存在
if not api_key:
    st.error("錯誤：找不到 OpenRouter API 金鑰。請在 .env 檔案中設定 OPENROUTER_API_KEY。")
    st.stop()

# --- 初始化 OpenAI 客戶端，但指向 OpenRouter ---
try:
    client = OpenAI(
      base_url="https://openrouter.ai/api/v1", # 這是關鍵，我們把請求指向 OpenRouter
      api_key=api_key,
    )
except Exception as e:
    st.error(f"客戶端初始化失敗，請檢查你的 API 金鑰。錯誤訊息：{e}")
    st.stop()

# --- 主應用程式介面 ---

st.title("😒 AI 毒雞湯大師 (通用版)")
st.markdown("生活不如意？工作不順心？來碗毒雞湯，保證你瞬間清醒。")
st.markdown("---")

user_problem = st.text_input("在這裡輸入你的煩惱，越具體越好：")

if st.button("給我一碗毒雞湯"):
    if user_problem:
        with st.spinner("大師正在熬製你的專屬毒雞湯..."):
            try:
                # --- AI 邏輯處理 (OpenAI 格式) ---
                # 這是與 AI 溝通的標準格式，包含「系統訊息」和「使用者訊息」
                response = client.chat.completions.create(
                  model="deepseek/deepseek-chat-v3-0324:free",  # 你可以在這裡換成任何 OpenRouter 支援的模型！
                  messages=[
                    {
                      "role": "system",
                      "content": "你是一個說話尖酸刻薄，但總能一針見血的「毒雞湯大師」。你的目標不是安慰人，而是用最犀利的語言點醒那些沉浸在自我感動中的人。你說話的風格：簡短、犀利、有點幽默、絕不同情。用繁體中文回答。"
                    },
                    {
                      "role": "user",
                      "content": user_problem
                    },
                  ]
                )
                
                # 從回應中提取文字
                ai_response = response.choices[0].message.content

                st.markdown("#### 大師開示：")
                st.info(ai_response)

            except Exception as e:
                st.error(f"糟糕，雞湯熬糊了...錯誤：{e}")
    else:
        st.warning("你連煩惱都懶得說，還想被點醒？")