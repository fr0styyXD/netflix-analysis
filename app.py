import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ═══════════════════════════════════════════════════════════
#                    PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Netflix Analysis Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Netflix theme
st.markdown("""
<style>
    .main {
        background-color: #141414;
    }
    .stMetric {
        background-color: #2d2d2d;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #404040;
    }
    .stMetric label {
        color: #ffffff !important;
    }
    h1 {
        color: #E50914;
    }
    h2, h3 {
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#                    LOAD DATA
# ═══════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    """Load and prepare Netflix data with caching for performance"""
    try:
        # Adjust path if needed
        df = pd.read_csv('data/netflix_cleaned.csv')

        # Ensure year_added column exists
        if 'year_added' not in df.columns:
            df['year_added'] = pd.to_datetime(df['date_added'], errors='coerce').dt.year

        return df
    except FileNotFoundError:
        st.error("❌ Error: netflix_cleaned.csv not found in data/ folder")
        st.stop()

# Load data
df = load_data()

# ═══════════════════════════════════════════════════════════
#                    HEADER
# ═══════════════════════════════════════════════════════════

st.title("🎬 Netflix Content Analysis Dashboard")
st.markdown("### Comprehensive analysis of 8,000+ Netflix titles revealing content strategy and market trends")
st.markdown("---")

# ═══════════════════════════════════════════════════════════
#                    SIDEBAR FILTERS
# ═══════════════════════════════════════════════════════════

st.sidebar.header("🎯 Filters & Controls")
st.sidebar.markdown("Use these filters to explore the data interactively")

# Content Type Filter
all_content_types = sorted(df['type'].dropna().unique().tolist())
selected_content_types = st.sidebar.multiselect(
    "📺 Content Type:",
    options=all_content_types,
    default=all_content_types  # you can set default; but user can clear it
)
if not selected_content_types:
    selected_content_types = all_content_types

# Rating Filter
all_ratings = sorted(df['rating'].dropna().unique().tolist())
selected_ratings = st.sidebar.multiselect(
    "⭐ Content Rating:",
    options=all_ratings,
    default=all_ratings
)
if not selected_ratings:
    selected_ratings = all_ratings

# Apply filters
filtered_df = df[
    (df['type'].isin(selected_content_types)) &
    (df['rating'].isin(selected_ratings))
]

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.info(f"**Showing {len(filtered_df):,} of {len(df):,} titles**")

# ═══════════════════════════════════════════════════════════
#                    KEY METRICS
# ═══════════════════════════════════════════════════════════

st.markdown("## 📊 Key Metrics at a Glance")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_titles = len(filtered_df)
    delta_titles = len(filtered_df) - len(df)
    st.metric(
        "Total Titles",
        f"{total_titles:,}",
        delta=f"{delta_titles:,}" if delta_titles != 0 else "All data"
    )

with col2:
    movies = len(filtered_df[filtered_df['type'] == 'Movie'])
    movies_pct = (movies / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.metric(
        "🎬 Movies",
        f"{movies:,}",
        delta=f"{movies_pct:.1f}%"
    )

with col3:
    shows = len(filtered_df[filtered_df['type'] == 'TV Show'])
    shows_pct = (shows / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.metric(
        "📺 TV Shows",
        f"{shows:,}",
        delta=f"{shows_pct:.1f}%"
    )

with col4:
    countries = filtered_df['country'].dropna().str.split(', ').explode().nunique()
    st.metric(
        "🌍 Countries",
        f"{countries:,}"
    )

st.markdown("---")

# ═══════════════════════════════════════════════════════════
#                    VISUALIZATION 1: CONTENT TYPE
# ═══════════════════════════════════════════════════════════

st.markdown("## 📺 Content Type Distribution")

col_viz1, col_insight1 = st.columns([2, 1])

with col_viz1:
    fig1, ax1 = plt.subplots(figsize=(10, 6), facecolor='#141414')
    ax1.set_facecolor('#1f1f1f')

    type_counts = filtered_df['type'].value_counts()
    colors = ['#E50914', '#564d4d']

    bars = type_counts.plot(
        kind='bar',
        ax=ax1,
        color=colors,
        edgecolor='white',
        linewidth=1.5
    )

    ax1.set_title('Movies vs TV Shows Distribution',
                  fontsize=16, fontweight='bold', color='white', pad=20)
    ax1.set_xlabel('Content Type', fontsize=12, fontweight='bold', color='white')
    ax1.set_ylabel('Number of Titles', fontsize=12, fontweight='bold', color='white')
    ax1.tick_params(colors='white')
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=0, color='white')

    # Add value labels on bars
    for i, v in enumerate(type_counts):
        ax1.text(i, v + 50, f'{v:,}', ha='center', fontweight='bold',
                 fontsize=14, color='white')

    # Style spines
    for spine in ax1.spines.values():
        spine.set_color('white')

    plt.tight_layout()
    st.pyplot(fig1)
    plt.close()

with col_insight1:
    st.markdown("### 💡 Key Insights")

    if len(type_counts) > 0:
        movies_count = type_counts.get('Movie', 0)
        shows_count = type_counts.get('TV Show', 0)
        total = movies_count + shows_count

        if total > 0:
            movies_pct = (movies_count / total) * 100

            st.write(f"📊 **Movies:** {movies_count:,} ({movies_pct:.1f}%)")
            st.write(f"📺 **TV Shows:** {shows_count:,} ({100-movies_pct:.1f}%)")

            if movies_pct > 65:
                st.success("✅ Strong focus on movie content")
            elif movies_pct < 35:
                st.info("📺 Heavy focus on TV series")
            else:
                st.info("⚖️ Balanced content mix")

st.markdown("---")

# ═══════════════════════════════════════════════════════════
#                    VISUALIZATION 2: TOP COUNTRIES
# ═══════════════════════════════════════════════════════════

st.markdown("## 🌍 Top 10 Content Producing Countries")

# Process countries
countries_list = []
for country_str in filtered_df['country'].dropna():
    if pd.notna(country_str):
        countries_list.extend([c.strip() for c in str(country_str).split(',')])

if countries_list:
    country_counts = pd.Series(countries_list).value_counts().head(10)

    fig2, ax2 = plt.subplots(figsize=(12, 7), facecolor='#141414')
    ax2.set_facecolor('#1f1f1f')

    country_counts.plot(
        kind='barh',
        ax=ax2,
        color='#E50914',
        edgecolor='white',
        linewidth=1.2
    )

    ax2.set_title('Top 10 Content Producing Countries',
                  fontsize=16, fontweight='bold', color='white', pad=20)
    ax2.set_xlabel('Number of Titles', fontsize=12, fontweight='bold', color='white')
    ax2.set_ylabel('Country', fontsize=12, fontweight='bold', color='white')
    ax2.tick_params(colors='white')

    # Add value labels
    for i, v in enumerate(country_counts):
        ax2.text(v + 20, i, f'{v:,}', va='center', fontweight='bold',
                 fontsize=11, color='white')

    # Style spines
    for spine in ax2.spines.values():
        spine.set_color('white')

    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

    # Insight
    top_country = country_counts.index[0]
    top_count = country_counts.iloc[0]
    top_pct = (top_count / len(countries_list)) * 100

    st.info(f"🏆 **{top_country}** dominates with **{top_count:,}** titles ({top_pct:.1f}% of all content)")

st.markdown("---")

# ═══════════════════════════════════════════════════════════
#                    VISUALIZATION 3: YEARLY TREND
# ═══════════════════════════════════════════════════════════

st.markdown("## 📈 Content Addition Trend Over Years")

yearly_data = filtered_df.groupby('year_added').size().sort_index()

if len(yearly_data) > 0:
    fig3, ax3 = plt.subplots(figsize=(14, 7), facecolor='#141414')
    ax3.set_facecolor('#1f1f1f')

    ax3.plot(yearly_data.index, yearly_data.values,
             marker='o', color='#E50914', linewidth=3, markersize=10)
    ax3.fill_between(yearly_data.index, yearly_data.values, alpha=0.3, color='#E50914')

    ax3.set_title('Netflix Content Addition Timeline',
                  fontsize=16, fontweight='bold', color='white', pad=20)
    ax3.set_xlabel('Year', fontsize=12, fontweight='bold', color='white')
    ax3.set_ylabel('Titles Added', fontsize=12, fontweight='bold', color='white')
    ax3.tick_params(colors='white')
    ax3.grid(True, alpha=0.2, linestyle='--', color='white')

    # Highlight peak year
    peak_year = yearly_data.idxmax()
    peak_value = yearly_data.max()

    ax3.annotate(f'Peak: {int(peak_value)} titles',
                 xy=(peak_year, peak_value),
                 xytext=(peak_year - 1, peak_value + 300),
                 arrowprops=dict(arrowstyle='->', color='white', lw=2),
                 fontsize=13, fontweight='bold', color='white',
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='#E50914', alpha=0.8))

    # Style spines
    for spine in ax3.spines.values():
        spine.set_color('white')

    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()

    # Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📅 Peak Year", f"{int(peak_year)}", f"{int(peak_value)} titles")

    with col2:
        if len(yearly_data) >= 3:
            recent_growth = ((yearly_data.iloc[-1] - yearly_data.iloc[-3]) / yearly_data.iloc[-3]) * 100
            st.metric("📊 Recent Trend (2 years)", f"{recent_growth:+.1f}%")

st.markdown("---")

# ═══════════════════════════════════════════════════════════
#                    VISUALIZATIONS 4 & 5: RATINGS & GENRES
# ═══════════════════════════════════════════════════════════

st.markdown("## 🎯 Content Ratings & Popular Genres")

col_left, col_right = st.columns(2)

# RATING DISTRIBUTION
with col_left:
    st.markdown("### ⭐ Rating Distribution")

    fig4, ax4 = plt.subplots(figsize=(10, 6), facecolor='#141414')
    ax4.set_facecolor('#1f1f1f')

    rating_counts = filtered_df['rating'].value_counts().sort_values()

    rating_counts.plot(
        kind='barh',
        ax=ax4,
        color='#564d4d',
        edgecolor='white',
        linewidth=1.2
    )

    ax4.set_title('Content by Rating Category',
                  fontsize=14, fontweight='bold', color='white')
    ax4.set_xlabel('Number of Titles', fontsize=11, color='white')
    ax4.set_ylabel('Rating', fontsize=11, color='white')
    ax4.tick_params(colors='white')

    for spine in ax4.spines.values():
        spine.set_color('white')

    plt.tight_layout()
    st.pyplot(fig4)
    plt.close()

    if len(rating_counts) > 0:
        top_rating = filtered_df['rating'].value_counts().index[0]
        st.info(f"Most common: **{top_rating}**")

# GENRE DISTRIBUTION
with col_right:
    st.markdown("### 🎭 Top 10 Genres")

    genres_list = []
    for genre_str in filtered_df['listed_in'].dropna():
        if pd.notna(genre_str):
            genres_list.extend([g.strip() for g in str(genre_str).split(',')])

    if genres_list:
        genre_counts = pd.Series(genres_list).value_counts().head(10)

        fig5, ax5 = plt.subplots(figsize=(10, 6), facecolor='#141414')
        ax5.set_facecolor('#1f1f1f')

        genre_counts.plot(
            kind='barh',
            ax=ax5,
            color='#E50914',
            edgecolor='white',
            linewidth=1.2
        )

        ax5.set_title('Most Popular Genres',
                      fontsize=14, fontweight='bold', color='white')
        ax5.set_xlabel('Number of Titles', fontsize=11, color='white')
        ax5.set_ylabel('Genre', fontsize=11, color='white')
        ax5.tick_params(colors='white')

        for spine in ax5.spines.values():
            spine.set_color('white')

        plt.tight_layout()
        st.pyplot(fig5)
        plt.close()

        top_genre = genre_counts.index[0]
        top_genre_count = genre_counts.iloc[0]
        st.info(f"Most popular: **{top_genre}** ({top_genre_count} titles)")

st.markdown("---")

# ═══════════════════════════════════════════════════════════
#                    KEY FINDINGS SUMMARY
# ═══════════════════════════════════════════════════════════

st.markdown("## 💡 Key Findings & Strategic Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 Content Strategy")
    st.write(f"- **{len(df):,}** totaltitles analyzed")
    st.write(f"- Content from {df['country'].dropna().str.split(', ').explode().nunique()} countries")
    if 'year_added' in df.columns and df['year_added'].notna().any():
        year_span = int(df['year_added'].max() - df['year_added'].min())
        st.write(f"- Spanning {year_span} years of data")

with col2:
    st.markdown("### 🌍 Geographic Leaders")
    if countries_list:
        top_3 = pd.Series(countries_list).value_counts().head(3)
        for idx, (country, count) in enumerate(top_3.items(), 1):
            st.write(f"{idx}. {country}: {count:,} titles")

with col3:
    st.markdown("### 📈 Growth Insights")
    if len(yearly_data) > 0:
        st.write(f"- Peak year: {int(yearly_data.idxmax())}")
        st.write(f"- Peak titles: {int(yearly_data.max()):,}")
        if len(yearly_data) >= 3:
            recent_trend = ((yearly_data.iloc[-1] - yearly_data.iloc[-3]) / yearly_data.iloc[-3]) * 100
            trend_emoji = "📈" if recent_trend > 0 else "📉"
            st.write(f"- Recent trend: {trend_emoji} {recent_trend:+.1f}%")

st.markdown("---")

# ═══════════════════════════════════════════════════════════
#                    DATA EXPLORER (OPTIONAL)
# ═══════════════════════════════════════════════════════════

with st.expander("🔍 Explore Raw Data"):
    st.markdown("### Sample of Filtered Data")
    st.dataframe(
        filtered_df[['title', 'type', 'country', 'release_year', 'rating', 'listed_in']].head(100),
        use_container_width=True
    )
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name='netflix_filtered_data.csv',
        mime='text/csv',
    )

# ═══════════════════════════════════════════════════════════
#                    FOOTER
# ═══════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px;'>
    <h3 style='color: #E50914;'>📊 Netflix Content Analysis Dashboard</h3>
    <h4 style='color: white;'>Created by Aksh Dhingra</h4>
    <p style='color: #999;'>
        📧 <a href='mailto:workdhingra26@gmail.com' style='color: #E50914;'>workdhingra26@gmail.com</a> | 
        💼 <a href='https://www.linkedin.com/in/akshdhingra' style='color: #E50914;'>LinkedIn</a> | 
        🐙 <a href='https://www.github.com/fr0styyXD' style='color: #E50914;'>GitHub</a>
    </p>
    <p style='color: #999;'><i>Built with Python • Pandas • Matplotlib • Seaborn • Streamlit</i></p>
    <p style='color: #666; font-size: 12px; margin-top: 20px;'>
        Data Source: Kaggle Netflix Movies and TV Shows Dataset | 
        Analysis Date: November 2025
    </p>
</div>
""", unsafe_allow_html=True)
