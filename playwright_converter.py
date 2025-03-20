import os
import asyncio
from markdown import markdown
from playwright.async_api import async_playwright
#
async def convert_markdown_to_pdf():
    # 获取当前目录下"answer"文件夹的路径
    answer_dir = os.path.join(os.getcwd(), 'answer')
    
    # 检查answer目录是否存在
    if not os.path.isdir(answer_dir):
        print(f"错误: 目录 {answer_dir} 不存在。")
        return
    
    # 查找answer目录中所有的.md文件
    md_files = [f for f in os.listdir(answer_dir) if f.endswith('.md')]
    
    if not md_files:
        print(f"在 {answer_dir} 中未找到Markdown文件。")
        return
    
    print(f"找到 {len(md_files)} 个Markdown文件。正在转换为PDF...")
    
    # 使用Playwright启动浏览器
    async with async_playwright() as p:
        # 启动浏览器（可选择 chromium, firefox, webkit）
        browser = await p.chromium.launch()
        
        # 转换每个Markdown文件为PDF
        for md_file in md_files:
            md_path = os.path.join(answer_dir, md_file)
            html_path = os.path.join(answer_dir, os.path.splitext(md_file)[0] + '.html')
            pdf_path = os.path.join(answer_dir, os.path.splitext(md_file)[0] + '.pdf')
            
            try:
                # 读取Markdown内容
                with open(md_path, encoding='utf-8') as f:
                    text = f.read()
                    
                # 检查Markdown中是否存在"✅"
                if "✅" in text:
                    print(f"在 {md_file} 中发现 ✅")
                
                # 将Markdown转换为HTML
                html_content = markdown(text, extensions=['extra'])
                
                # 检查转换后的HTML中是否仍存在"✅"
                if "✅" in html_content:
                    print(f"在 {md_file} 的markdown转换后仍存在 ✅")
                else:
                    print(f"警告: 在 {md_file} 的markdown转换过程中 ✅ 丢失了")
                
                # 添加基本样式，使PDF更美观，并支持中文
                styled_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC&family=Noto+Color+Emoji&display=swap');
                        body {{
                            font-family: 'Noto Sans SC', Arial, sans-serif;
                            margin: 40px;
                            line-height: 1.6;
                        }}
                        h1, h2, h3 {{ color: #333; }}
                        code {{ background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px; }}
                        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                        blockquote {{ border-left: 4px solid #ddd; padding-left: 20px; color: #555; }}
                        img {{ max-width: 100%; }}
                        table {{ border-collapse: collapse; width: 100%; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
                </html>
                """
                
                # 保存中间HTML文件
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(styled_html)
                    print(f"保存中间HTML文件: {html_path}")
                
                # 检查最终HTML中是否存在"✅"
                if "✅" in styled_html:
                    print(f"{md_file}的HTML文件中存在 ✅")
                else:
                    print(f"警告: {md_file}的HTML文件中未找到 ✅")
                
                # 创建新页面并导航到HTML文件
                page = await browser.new_page()
                await page.goto(f"file://{os.path.abspath(html_path)}")
                
                # 等待页面加载完成
                await page.wait_for_load_state("networkidle")
                
                # 导出为PDF
                await page.pdf(path=pdf_path, format="A4", margin={
                    "top": "1cm",
                    "right": "1cm",
                    "bottom": "1cm",
                    "left": "1cm"
                })
                
                await page.close()
                print(f"成功将 {md_file} 转换为PDF。")
                
            except Exception as e:
                print(f"转换 {md_file} 时出错: {str(e)}")
        
        # 关闭浏览器
        await browser.close()

# 运行异步函数的入口点
if __name__ == "__main__":
    asyncio.run(convert_markdown_to_pdf())