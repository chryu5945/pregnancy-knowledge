import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import json

# Load env
load_dotenv()

# Use relative paths for compatibility with Streamlit Cloud
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")
DATA_PATH = os.path.join(BASE_DIR, "data", "videos.json")
COLLECTION_NAME = "pregnancy_knowledge"

def get_embedding_function():
    openai_api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")
    return embedding_functions.OpenAIEmbeddingFunction(
        api_key=openai_api_key,
        model_name="text-embedding-3-small"
    )

def query_database(query_text, n_results=5):
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    embedding_fn = get_embedding_function()
    collection = client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)
    
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    
    return results

def generate_answer(query, context_texts):
    # Try fetching from Streamlit secrets first, then environment variable
    api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    context = "\n\n".join(context_texts)
    
    prompt = f"""
    당신은 육아 및 출산 전문가입니다. 아래의 [정보]를 바탕으로 사용자의 질문에 답변해주세요.
    
    [정보]는 유튜브 영상의 제목과 설명(Description)입니다. 자막 전체가 아닐 수 있습니다.
    따라서 정보가 충분하지 않다면, 제공된 [정보]의 영상 제목을 인용하여 "이 영상에서 관련 내용을 확인하실 수 있습니다"라고 안내하고,
    일반적인 의학 지식을 덧붙여 설명해주세요.
    
    [정보]
    {context}
    
    [질문]
    {query}
    
    [답변]
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "도움이 되는 친절한 육아 전문가입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

def load_video_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    st.set_page_config(page_title="육아/출산 지식 도우미", layout="wide")
    
    st.title("👶 삐뽀삐뽀 육아 지식 검색")
    st.markdown("유튜브 '하정훈의 삐뽀삐뽀 119' 채널 기반 지식 시스템입니다.")
    
    # Create Tabs
    tab1, tab2 = st.tabs(["🔍 지식 검색 (RAG)", "📋 전체 영상 목록"])
    
    # --- Tab 1: RAG Search ---
    with tab1:
        # Sidebar for Categories/Keywords (moved inside tab or kept global? kept global for simple layout but contextually it fits search)
        # For this request, I'll keep the sidebar simple or move category selection here.
        # Let's keep the original search logic structure but inside this tab.
        
        st.subheader("궁금한 점을 물어보세요")
        
        categories = ["신생아", "이유식", "수면교육", "예방접종", "응급처치"]
        selected_category = st.radio("카테고리 선택", ["전체"] + categories, horizontal=True)
        
        query = st.text_input("질문 입력 (예: 열이 날 때 어떻게 하나요?)")
        
        if st.button("검색") or query:
            if not query and selected_category != "전체":
                query = f"{selected_category} 관련 정보 알려줘"
                
            if query:
                with st.spinner("지식을 검색 중입니다..."):
                    results = query_database(query)
                    
                    if results and results['documents']:
                        documents = results['documents'][0]
                        metadatas = results['metadatas'][0]
                        
                        answer = generate_answer(query, documents)
                        
                        st.markdown("### 💡 답변")
                        st.write(answer)
                        
                        st.markdown("---")
                        st.markdown("### 📚 관련 영상 정보")
                        
                        seen_urls = set()
                        for i, doc in enumerate(documents):
                            meta = metadatas[i]
                            url = meta['url']
                            title = meta['title']
                            start_time = int(meta['start_time'])
                            
                            link = f"{url}&t={start_time}s"
                            
                            if url not in seen_urls:
                                st.markdown(f"**[{title}]({link})**")
                                st.caption(f"관련 내용: {doc[:100]}...")
                                seen_urls.add(url)
                    else:
                        st.warning("관련된 정보를 찾을 수 없습니다.")

    # --- Tab 2: Video List ---
    with tab2:
        st.subheader("전체 영상 라이브러리")
        
        videos = load_video_data()
        
        if not videos:
            st.error("영상 데이터가 없습니다.")
        else:
            # Create DataFrame for display
            df = pd.DataFrame(videos)
            
            # Select columns to display
            display_df = df[['title', 'url']].copy()
            display_df.columns = ['제목', '유튜브 링크']
            
            # Use dataframe with selection
            event = st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # Check for selection
            if event.selection.rows:
                selected_index = event.selection.rows[0]
                selected_video = videos[selected_index]
                
                st.divider()
                st.markdown(f"### 📺 {selected_video['title']}")
                st.markdown(f"**링크**: [YouTube에서 보기]({selected_video['url']})")
                
                # Show transcript preview or summary if available
                if 'transcript' in selected_video and selected_video['transcript']:
                    st.markdown("#### 📝 자막 미리보기 (초반 5문장)")
                    transcript_text = ""
                    for item in selected_video['transcript'][:5]:
                        transcript_text += f"- ({int(item['start'])}초) {item['text']}\n"
                    st.text(transcript_text)
                    
                    with st.expander("자막 전체 보기"):
                        full_text = " ".join([item['text'] for item in selected_video['transcript']])
                        st.write(full_text)
                else:
                    st.info("자막 데이터가 없습니다.")

if __name__ == "__main__":
    main()
