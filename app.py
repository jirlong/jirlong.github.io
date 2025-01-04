import streamlit as st
import jieba
import pandas as pd
from collections import Counter
import re
import csv
from io import StringIO

# 設定頁面配置
st.set_page_config(
    page_title="中文分詞工具",
    layout="wide"
)

def load_stopwords(file_path):
    """載入停用詞"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        st.warning(f"找不到停用詞檔案：{file_path}")
        return set()

def load_user_dict(file_path):
    """載入自定義詞典"""
    try:
        jieba.load_userdict(file_path)
    except FileNotFoundError:
        st.warning(f"找不到自定義詞典：{file_path}")

# 載入停用詞和自定義詞典
STOPWORDS = load_stopwords('data/stopwords_zh-tw.txt')
load_user_dict('data/userdict.txt')

def remove_punctuation_and_english(text):
    """移除標點符號、英文字母和數字"""
    # 移除中文標點符號
    text = re.sub(r'[\u3000-\u303F\uFF00-\uFFEF]', '', text)
    # 移除英文標點符號
    text = re.sub(r'[^\u4e00-\u9fff\s]', '', text)
    return text

def process_text(text, remove_stopwords=True):
    """處理文本，進行分詞並選擇性地移除停用詞"""
    # 清理文本
    text = remove_punctuation_and_english(text)
    
    # 使用結巴分詞
    tokens = list(jieba.cut(text))
    
    # 移除空字串
    tokens = [token for token in tokens if token.strip()]
    
    if remove_stopwords:
        tokens = [token for token in tokens if token not in STOPWORDS]
    
    return tokens

def process_paragraphs(text, remove_stopwords=True):
    """處理多個段落的文本"""
    # 依據換行符分割段落
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    # 處理每個段落
    processed_paragraphs = []
    all_tokens = []
    
    for paragraph in paragraphs:
        tokens = process_text(paragraph, remove_stopwords)
        if tokens:  # 只加入非空的結果
            processed_paragraphs.append(tokens)
            all_tokens.extend(tokens)
    
    return processed_paragraphs, all_tokens

def calculate_statistics(tokens):
    """計算文本統計信息"""
    # 計算詞頻
    word_freq = Counter(tokens)
    
    # 轉換成 DataFrame 以便顯示
    df = pd.DataFrame(word_freq.most_common(), columns=['詞語', '出現次數'])
    
    return {
        'total_tokens': len(tokens),
        'unique_tokens': len(set(tokens)),
        'word_freq': df
    }

def create_download_csv(processed_paragraphs):
    """建立下載用的 CSV 內容"""
    output = StringIO()
    writer = csv.writer(output)
    # 每個段落寫入一行，詞語用逗號分隔
    for paragraph_tokens in processed_paragraphs:
        writer.writerow(paragraph_tokens)
    return output.getvalue()

def main():
    # 標題
    st.title("中文分詞工具 🔤")
    
    # 側邊欄設置
    with st.sidebar:
        st.header("設定")
        remove_stopwords = st.checkbox("移除停用詞", value=True)
        show_statistics = st.checkbox("顯示統計資訊", value=True)
        
        st.header("說明")
        st.markdown("""
        這是一個基於 jieba 的中文分詞工具。
        
        功能：
        - 支援多段落中文分詞
        - 自動載入自定義詞典
        - 自動載入停用詞列表
        - 自動移除標點符號、英文和數字
        - 提供文本統計分析
        - 詞頻統計與視覺化
        - 分段落顯示分詞結果
        - CSV 匯出支援多段落格式
        """)
    
    # 主要內容區
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # 文本輸入區
        text_input = st.text_area(
            "請輸入要分詞的文字（可輸入多個段落）：",
            height=200,
            placeholder="在此輸入中文文字...\n可以換行輸入多個段落..."
        )
        
        if text_input:
            # 進行分詞
            processed_paragraphs, all_tokens = process_paragraphs(text_input, remove_stopwords)
            
            # 顯示分詞結果
            st.header("分詞結果")
            for i, paragraph_tokens in enumerate(processed_paragraphs, 1):
                st.subheader(f"第 {i} 段")
                st.write(" | ".join(paragraph_tokens))
            
            # 提供下載按鈕
            csv_content = create_download_csv(processed_paragraphs)
            st.download_button(
                label="下載分詞結果",
                data=csv_content.encode('utf-8'),
                file_name='tokens.csv',
                mime='text/csv'
            )
    
    with col2:
        if text_input and show_statistics:
            # 計算並顯示統計信息
            stats = calculate_statistics(all_tokens)
            
            st.header("統計資訊")
            
            # 基本統計
            col_stats1, col_stats2 = st.columns(2)
            with col_stats1:
                st.metric("總詞數", stats['total_tokens'])
            with col_stats2:
                st.metric("不重複詞數", stats['unique_tokens'])
            
            # 詞頻統計表
            st.subheader("詞頻統計")
            st.dataframe(
                stats['word_freq'].head(10),
                use_container_width=True
            )
            
            # 詞頻視覺化
            if len(stats['word_freq']) > 0:
                st.subheader("詞頻分佈")
                chart_data = stats['word_freq'].head(10)
                st.bar_chart(
                    chart_data.set_index('詞語')['出現次數'],
                    use_container_width=True
                )

if __name__ == "__main__":
    main()