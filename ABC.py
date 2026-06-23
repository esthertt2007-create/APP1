import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Excel Data Analyzer", layout="wide")

st.title("📊 Excel Data Analyzer")
st.markdown("Upload an Excel file to visualize histograms and get statistical insights for numeric columns.")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

THRESHOLD = 0.05  # mean-median relative difference threshold for forecasting suitability

def is_forecast_suitable(mean_val, median_val):
    if mean_val == 0:
        return abs(mean_val - median_val) < 1e-9
    relative_diff = abs(mean_val - median_val) / abs(mean_val)
    return relative_diff <= THRESHOLD

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success(f"File loaded: {uploaded_file.name} — {df.shape[0]} rows × {df.shape[1]} columns")

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_cols:
            st.warning("No numeric columns found in the uploaded file.")
        else:
            st.markdown(f"### Numeric columns detected: `{'`, `'.join(numeric_cols)}`")
            st.divider()

            for col in numeric_cols:
                col_data = df[col].dropna()

                if col_data.empty:
                    st.warning(f"Column **{col}** has no valid numeric data. Skipping.")
                    continue

                mean_val = col_data.mean()
                median_val = col_data.median()
                suitable = is_forecast_suitable(mean_val, median_val)

                left, right = st.columns([2, 1])

                with left:
                    fig, ax = plt.subplots(figsize=(7, 4))
                    ax.hist(col_data, bins="auto", color="#4C72B0", edgecolor="white", alpha=0.85)
                    ax.axvline(mean_val, color="#DD4949", linestyle="--", linewidth=1.8, label=f"Mean: {mean_val:,.2f}")
                    ax.axvline(median_val, color="#2CA02C", linestyle="-.", linewidth=1.8, label=f"Median: {median_val:,.2f}")
                    ax.set_title(f"Histogram — {col}", fontsize=13, fontweight="bold")
                    ax.set_xlabel(col)
                    ax.set_ylabel("Frequency")
                    ax.legend()
                    ax.spines[["top", "right"]].set_visible(False)
                    st.pyplot(fig)
                    plt.close(fig)

                with right:
                    st.markdown(f"#### 📈 {col}")
                    st.metric("Mean", f"{mean_val:,.4f}")
                    st.metric("Median", f"{median_val:,.4f}")
                    rel_diff_pct = abs(mean_val - median_val) / abs(mean_val) * 100 if mean_val != 0 else 0
                    st.metric("Mean–Median Diff", f"{rel_diff_pct:.2f}%")

                    if suitable:
                        st.success("✅ The data can be used for forecasting.")
                    else:
                        st.warning("⚠️ Mean and median differ significantly — data may be skewed. Use caution for forecasting.")

                st.divider()

    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("👆 Upload an Excel file to get started.")
    st.markdown("""
    **What this app does:**
    - Detects all numeric columns in your Excel file
    - Plots a histogram for each numeric column
    - Calculates mean and median
    - Tells you if the data is suitable for forecasting (mean ≈ median, i.e., <5% relative difference)
    """)
