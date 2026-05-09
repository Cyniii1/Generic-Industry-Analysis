import streamlit as st
import os
import time
from datetime import datetime
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

# ==========================================
# 零、 安全脱敏配置 (从云端 Secrets 读取)
# ==========================================
if "DEEPSEEK_API_KEY" in st.secrets:
    DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
else:
    # 这里的默认值仅用于你本地测试，上传后云端会覆盖它
    DEEPSEEK_API_KEY = "sk-6e9424486d334aeb9f9c19e5c8aafa7c" 

current_year = datetime.now().year

# 行业库保持对齐
MACRO_TRENDS = ["新质生产力", "新型工业化", "数字中国", "绿色低碳转型", "产业链韧性与安全"]
SECTOR_INDUSTRIES = ["半导体制造设备", "先进封装技术", "工业具身智能机器人", "低空经济(eVTOL)", "固态电池产业链", "氢能制储加换", "商业航天与卫星", "五轴联动数控机床", "AI创新药研发", "合成生物学", "卫星互联网", "工业软件(EDA/CAE)", "第三代半导体材料", "量子计算应用", "智能座舱生态", "自动驾驶算法", "跨境电商DTC", "数据要素市场化", "液冷智算中心", "特高压输变电", "精密光学仪器", "碳纤维复合材料", "核聚变商业化", "生物芯片", "脑机接口"]

def run_analysis(target, is_macro):
    llm = LLM(
        model="openai/deepseek-v4-flash", 
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1",
        temperature=0.3,
        timeout=120,
        max_retries=3
    )
    
    @tool("Search")
    def search_tool(query: str):
        """实时搜索最新的政策、数据及行业研报。"""
        return DuckDuckGoSearchRun().run(query)

    researcher = Agent(
        role='首席产业情报官',
        goal=f'获取【{target}】在{current_year}年的核心数据。',
        backstory='你追求效率，只抓取事实，拒绝废话。',
        tools=[search_tool], llm=llm
    )

    analyst = Agent(
        role='产业链战略分析师',
        goal=f'撰写【{target}】的深度研报。',
        backstory='你擅长PESTEL分析与价值链拆解。',
        tools=[search_tool], llm=llm
    )

    task1 = Task(description=f"搜集{target}在{current_year}年的政策与数据。", expected_output="事实简报。", agent=researcher)
    task2 = Task(description=f"基于事实，撰写{target}的智库级内参报告。", expected_output="深度研报。", agent=analyst)

    crew = Crew(agents=[researcher, analyst], tasks=[task1, task2], process=Process.sequential)
    return crew.kickoff()

# UI 界面
st.set_page_config(page_title="泛行业宏观分析终端", page_icon="🏛️", layout="wide")
st.title("🏛️ 泛行业宏观量化分析终端 V5.1")

with st.sidebar:
    st.title("智库控制中心")
    mode = st.radio("🔍 模式", ["宏观趋势推演", "细分赛道分析"])
    selected_target = st.selectbox("🎯 目标", MACRO_TRENDS if mode=="宏观趋势推演" else SECTOR_INDUSTRIES)
    start_btn = st.button("🚀 启动深度推演", use_container_width=True)

if start_btn:
    with st.status(f"正在构建 【{selected_target}】 推演模型...", expanded=True) as status:
        try:
            result = run_analysis(selected_target, mode=="宏观趋势推演")
            status.update(label="✅ 推演报告生成成功！", state="complete")
            st.markdown("---")
            st.markdown(result)
            st.download_button("📥 下载报告", data=str(result), file_name=f"{selected_target}.md")
        except Exception as e:
            st.error(f"异常：{e}")