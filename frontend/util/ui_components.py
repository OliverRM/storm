import streamlit as st
import markdown

from util.text_processing import DemoTextProcessingHelper


class DemoUIHelper:
    @staticmethod
    def st_markdown_adjust_size(content, font_size=20):
        st.markdown(
            f"""
        <span style='font-size: {font_size}px;'>{content}</span>
        """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def get_article_card_UI_style(boarder_color="#9AD8E1"):
        return {
            "card": {
                "width": "100%",
                "height": "116px",
                "max-width": "640px",
                "background-color": "#FFFFF",
                "border": "1px solid #CCC",
                "padding": "20px",
                "border-radius": "5px",
                "border-left": f"0.5rem solid {boarder_color}",
                "box-shadow": "0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15)",
                "margin": "0px",
            },
            "title": {
                "white-space": "nowrap",
                "overflow": "hidden",
                "text-overflow": "ellipsis",
                "font-size": "17px",
                "color": "rgb(49, 51, 63)",
                "text-align": "left",
                "width": "95%",
                "font-weight": "normal",
            },
            "text": {
                "white-space": "nowrap",
                "overflow": "hidden",
                "text-overflow": "ellipsis",
                "font-size": "25px",
                "color": "rgb(49, 51, 63)",
                "text-align": "left",
                "width": "95%",
            },
            "filter": {"background-color": "rgba(0, 0, 0, 0)"},
        }

    @staticmethod
    def customize_toast_css_style():
        # Note padding is top right bottom left
        st.markdown(
            """
            <style>

                div[data-testid=stToast] {
                    padding: 20px 10px 40px 10px;
                    background-color: #FF0000;   /* red */
                    width: 40%;
                }

                [data-testid=toastContainer] [data-testid=stMarkdownContainer] > p {
                    font-size: 25px;
                    font-style: normal;
                    font-weight: 400;
                    color: #FFFFFF;   /* white */
                    line-height: 1.5; /* Adjust this value as needed */
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def article_markdown_to_html(article_title, article_content):
        return f"""
        <html>
            <head>
                <meta charset="utf-8">
                <title>{article_title}</title>
                <style>
                    .title {{
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <div class="title">
                    <h1>{article_title.replace('_', ' ')}</h1>
                </div>
                <h2>Table of Contents</h2>
                {DemoTextProcessingHelper.generate_html_toc(article_content)}
                {markdown.markdown(article_content)}
            </body>
        </html>
        """
