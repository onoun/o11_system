import streamlit as st
import pandas as pd
import base64
from io import BytesIO

def calculate_additional_quantity(sku_quantity):
    """
    商品数量に基づき、追加数量を計算
    5点: +1, 6点: +2、以降1点増えるごとに+1
    """
    if sku_quantity >= 5:
        return sku_quantity - 4
    else:
        return 0

def process_file(uploaded_file):
    df = pd.read_csv(uploaded_file)
    header = list(df.columns)
    result = []
    
    valid_sku_prefixes = ['dear-esc-1', 'dear-mcl-1', 'dear-fwa-1', 'dear-mlo-1', 'dear-des-1', 'dear-full-1','dear-ext-1']

    for _, row in df.iterrows():
        total_sku_quantity = 0
        
        for i in range(10):
            sku_col = f'SKU{i+1}'
            qty_col = f'商品数量{i+1}'
            
            if sku_col in row and qty_col in row:
                sku = row[sku_col]
                quantity = row[qty_col]
                
                if pd.notna(sku) and any(sku.startswith(prefix) for prefix in valid_sku_prefixes):
                    total_sku_quantity += quantity
        
        additional_quantity = calculate_additional_quantity(total_sku_quantity)
        
        row_with_additional = row.tolist() + [total_sku_quantity, additional_quantity]
        result.append(row_with_additional)
    
    new_columns = header + ['指定されたSKUの総数量', '追加数量']
    result_df = pd.DataFrame(result, columns=new_columns)
    
    return result_df

def download_link_excel(df, filename='output.xlsx'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)

    b64 = base64.b64encode(output.getvalue()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">Download Excel File</a>'
    return href

def main():
    st.title("SKU 集計と追加数量の計算")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        result_df = process_file(uploaded_file)
        
        if result_df is not None:
            total_additional_quantity = result_df['追加数量'].sum()
            st.write(f"追加数量の合計: {total_additional_quantity}")
            st.dataframe(result_df)
            st.markdown(download_link_excel(result_df), unsafe_allow_html=True)

if __name__ == "__main__":
    main()