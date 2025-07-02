# 導入必要的Python庫
import streamlit as st  # 用於創建網頁應用界面
from openai import OpenAI  # OpenAI官方庫，用於與AI模型交互
import os  # 用於操作系統環境變量
from dotenv import load_dotenv  # 用於加載.env文件中的環境變量

# --- 環境設定部分 ---

# 加載項目目錄下的.env文件，獲取其中定義的環境變量
load_dotenv()

# 從環境變量中獲取OpenRouter API密鑰
api_key = os.getenv("OPENROUTER_API_KEY")

# 檢查API密鑰是否存在，如果不存在則顯示錯誤並停止程序
if not api_key:
    st.error("錯誤：找不到 OpenRouter API 密鑰。請在 .env 文件中設定 OPENROUTER_API_KEY。")
    st.stop()  # 停止Streamlit應用運行

# --- 初始化OpenAI客戶端，但實際連接到OpenRouter服務 ---
try:
    # 創建OpenAI客戶端實例，但將請求重定向到OpenRouter
    client = OpenAI(
      base_url="https://openrouter.ai/api/v1",  # 關鍵設置：將請求發送到OpenRouter而非OpenAI
      api_key=api_key,  # 使用從.env文件獲取的API密鑰
    )
except Exception as e:
    # 如果初始化失敗，顯示錯誤信息並停止程序
    st.error(f"客戶端初始化失敗，請檢查你的 API 密鑰。錯誤信息：{e}")
    st.stop()

# --- 主應用程序界面 ---

# 設置網頁標題和描述
st.title("😒 AI 毒雞湯大師 (通用版)")  # 主標題
st.markdown("生活不如意？工作不順心？來碗毒雞湯，保證你瞬間清醒。")  # 副標題
st.markdown("---")  # 分隔線

# 創建文本輸入框，讓用戶輸入煩惱
user_problem = st.text_input("在這裡輸入你的煩惱，越具體越好：")

# 創建按鈕，點擊後生成毒雞湯
if st.button("給我一碗毒雞湯"):
    if user_problem:  # 檢查用戶是否輸入了內容
        # 顯示加載動畫
        with st.spinner("大師正在熬製你的專屬毒雞湯..."):
            try:
                # --- AI邏輯處理部分 ---
                # 向AI模型發送請求，獲取響應
                response = client.chat.completions.create(
                  model="deepseek/deepseek-chat-v3-0324:free",  # 指定使用的AI模型
                  messages=[
                    {
                      "role": "system",  # 系統消息，定義AI的角色和行為
                      "content": "你是一個說話尖酸刻薄，但總能一針見血的「毒雞湯大師」。你的目標不是安慰人，而是用最犀利的語言點醒那些沉浸在自我感動中的人。你說話的風格：簡短、犀利、有點幽默、絕不同情。用繁體中文回答。"
                    },
                    {
                      "role": "user",  # 用戶消息，包含用戶輸入的煩惱
                      "content": user_problem
                    },
                  ]
                )
                
                # 從響應中提取AI生成的文本內容
                ai_response = response.choices[0].message.content

                # 顯示AI生成的毒雞湯
                st.markdown("#### 大師開示：")  # 小標題
                st.info(ai_response)  # 用信息框顯示內容

            except Exception as e:
                # 如果出現錯誤，顯示錯誤信息
                st.error(f"糟糕，雞湯熬糊了...錯誤：{e}")
    else:
        # 如果用戶沒有輸入內容，顯示警告
        st.warning("你連煩惱都懶得說，還想被點醒？")
