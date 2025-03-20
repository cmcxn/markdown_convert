import os
import sys
import tempfile
from playwright.sync_api import sync_playwright
import pypandoc

def convert_markdown_to_pdf_sync(md_content: str) -> str:
    """Converts Markdown content to PDF using Playwright synchronously."""

    with tempfile.TemporaryDirectory() as temp_dir:
        html_path = os.path.join(temp_dir, "temp.html")
        pdf_path = os.path.join(temp_dir, "output.pdf")

        html_content = pypandoc.convert_text(
            md_content,
            "html",
            format="markdown",
            extra_args=["--standalone"],
        )

        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC&family=Noto+Color+Emoji&display=swap');
                body {{
                    font-family: 'Noto Sans SC', 'Noto Color Emoji', Arial, sans-serif;
                    margin: 40px;
                    line-height: 1.6;
                }}
                h1, h2, h3 {{ color: #333; }}
                code {{ background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px; }}
                pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                blockquote {{ border-left: 4px solid #ddd; padding-left: 20px; color: #555; }}
                img {{ max-width: 100%; }}
                table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(styled_html)

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"file://{os.path.abspath(html_path)}")
            page.wait_for_load_state("networkidle")
            page.pdf(
                path=pdf_path,
                format="A4",
                margin={
                    "top": "1cm",
                    "right": "1cm",
                    "bottom": "1cm",
                    "left": "1cm",
                },
            )
            browser.close()
        return pdf_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pdf_converter.py <markdown_file>")
        sys.exit(1)

    markdown_file = sys.argv[1]

    try:
        with open(markdown_file, "r", encoding="utf-8") as f:
            md_content = f.read()

        pdf_path = convert_markdown_to_pdf_sync(md_content)
        print(pdf_path)  # Print the PDF path to stdout
    except Exception as e:
        print(f"Error during PDF conversion: {e}", file=sys.stderr)
        sys.exit(1)