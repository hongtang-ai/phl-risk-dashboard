import streamlit as st


def inject_phl_theme():
    """统一注入 Tailwind + 自定义样式（彻底解决弃用警告）"""
    html_content = """
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            content: ["./**/*.{html,js}"],
            theme: {
                extend: {
                    colors: {
                        phl: {
                            primary: "#00E5CC",
                            accent: "#A78BFA",
                            dark: "#0A0A0A",
                            card: "#161618"
                        }
                    }
                }
            }
        }
    </script>
    <style>
        .stApp {
            background-color: #0A0A0A;
        }
        .glass-card {
            background: rgba(22, 22, 24, 0.85);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255,255,255,0.08);
        }
        .hover-lift:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 
                       0 8px 10px -6px rgb(0 0 0 / 0.1);
        }
    </style>
    """
    # 使用 st.html（2026 年推荐方式）
    st.html(html_content)
