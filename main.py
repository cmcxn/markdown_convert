import os
import asyncio
import tempfile
from typing import Optional

import pypandoc
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from playwright.async_api import async_playwright
import sys
import multiprocessing
import subprocess

app = FastAPI()

# Serve static files (like CSS, JavaScript)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates directory
templates = Jinja2Templates(directory="templates")


async def convert_markdown_to_pdf(md_content: str, base_url: str) -> str:
    """Converts Markdown content to PDF using Playwright."""
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

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(f"file://{os.path.abspath(html_path)}")
            await page.wait_for_load_state("networkidle")
            await page.pdf(
                path=pdf_path,
                format="A4",
                margin={
                    "top": "1cm",
                    "right": "1cm",
                    "bottom": "1cm",
                    "left": "1cm",
                },
            )
            await browser.close()
        return pdf_path


def convert_markdown_to_html(md_content: str) -> str:
    """Converts Markdown content to HTML using pypandoc."""
    html_content = pypandoc.convert_text(
        md_content, "html", format="markdown", extra_args=["--standalone"]
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
    return styled_html


def convert_markdown_to_pdf_sync(md_content: str) -> str:
    """Converts Markdown content to PDF using Playwright synchronously."""
    import os
    import tempfile
    from playwright.sync_api import sync_playwright

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


@app.post("/convert")
async def convert(
    request: Request,
    file: UploadFile = File(...),
    output_format: str = Form(...),
):
    """Converts the uploaded Markdown file to the specified format."""
    try:
        contents = await file.read()
        md_content = contents.decode("utf-8")

        if output_format == "html":
            html_content = convert_markdown_to_html(md_content)
            return HTMLResponse(content=html_content)
        elif output_format == "pdf":
            # Create a temporary file to pass the Markdown content to the subprocess
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as temp_file:
                temp_file.write(md_content)
                temp_file_path = temp_file.name

            try:
                # Run the synchronous PDF conversion in a separate process
                result = subprocess.run(
                    [
                        sys.executable,  # Path to the current Python interpreter
                        "pdf_converter.py",  # Script to run
                        temp_file_path,  # Input Markdown file
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                pdf_path = result.stdout.strip()

                if not os.path.exists(pdf_path):
                    raise Exception(f"PDF conversion failed: {result.stderr}")

                return FileResponse(
                    pdf_path,
                    media_type="application/pdf",
                    filename=file.filename.replace(".md", ".pdf"),
                )

            except subprocess.CalledProcessError as e:
                return JSONResponse(
                    {"error": f"PDF conversion failed: {e.stderr}"}, status_code=500
                )
            finally:
                # Clean up the temporary file
                os.remove(temp_file_path)

        else:
            return JSONResponse({"error": "Invalid output format"}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serves the HTML form."""
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)