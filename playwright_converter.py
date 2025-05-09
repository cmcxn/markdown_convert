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

app = FastAPI()

# Serve static files (like CSS, JavaScript)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates directory
templates = Jinja2Templates(directory="templates")


async def convert_markdown_to_pdf(md_content: str) -> str:
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


@app.post("/convert")
async def convert(
    request: Request,
    file: UploadFile = File(...),
    output_format: str = Form(...),
):
    """Converts the uploaded Markdown file to the specified format."""
    try:
        try:
            contents = await file.read()
            md_content = contents.decode("utf-8")
        except UnicodeDecodeError as e:
            return JSONResponse(
                {"error": f"Encoding error: {str(e)}.  Please ensure the file is UTF-8 encoded."},
                status_code=400,
            )


        if output_format == "html":
            html_content = convert_markdown_to_html(md_content)
            return HTMLResponse(content=html_content)
        elif output_format == "pdf":
            try:
                pdf_path = await convert_markdown_to_pdf(md_content)
                return FileResponse(
                    pdf_path,
                    media_type="application/pdf",
                    filename=file.filename.replace(".md", ".pdf"),
                )
            except Exception as e:
                return JSONResponse(
                    {"error": f"PDF conversion failed: Error during PDF conversion: {str(e)}"},
                    status_code=500,
                )
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